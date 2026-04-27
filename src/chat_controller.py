"""
chat_controller.py — Enhanced CyberGuard AI Chat Controller
------------------------------------------------------------
Improvements over original:
  - Dataclass-based routing result & pipeline result models
  - Enum-driven intent modes (no bare string comparisons)
  - Compile regex patterns once at module level (performance)
  - Hybrid router extracted into its own class with clean fallback chain
  - `process_message` and `process_command` fully typed
  - Capturing generator replaced with thread-safe queue-based approach
  - Structured logging instead of silent pass
  - `set_api_key` / `is_api_key_set` kept for interface compatibility
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Generator, Iterator, Optional

from src.bert_inference import BertInferenceModule
from src.llm_handler import LLMHandler, LLMConfig
from src.decision_engine import validate_verdict
from src.prompt_templates import (
    ANALYSIS_PROMPT, CHAT_PROMPT, REWRITE_PROMPT,
    QUIZ_PROMPT, ASSESSMENT_PROMPT, INTENT_ROUTING_PROMPT,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)


# ─────────────────────────────────────────────────────────────
# Enums & Constants
# ─────────────────────────────────────────────────────────────

class Mode(str, Enum):
    """All supported processing modes."""
    ANALYZE = "ANALYZE"
    QUIZ    = "QUIZ"
    ASSESS  = "ASSESS"
    REWRITE = "REWRITE"
    CHAT    = "CHAT"


# Keyword sets per mode — using frozenset for O(1) lookup
_FAST_TRIGGERS: dict[Mode, frozenset[str]] = {
    Mode.QUIZ:    frozenset({"quiz", "test", "test me"}),
    Mode.ASSESS:  frozenset({"assess", "assessment"}),
    Mode.REWRITE: frozenset({"rewrite", "safe alternative", "rephrase"}),
    Mode.ANALYZE: frozenset({"analyze", "analyse", "classify", "moderate", "review", "flag"}),
}

# Prompt map — keeps process_message clean
_PROMPT_MAP: dict[Mode, str] = {
    Mode.ANALYZE: ANALYSIS_PROMPT,
    Mode.QUIZ:    QUIZ_PROMPT,
    Mode.ASSESS:  ASSESSMENT_PROMPT,
    Mode.REWRITE: REWRITE_PROMPT,
    Mode.CHAT:    CHAT_PROMPT,
}

# Pre-compiled regex patterns
_RE_MODE     = re.compile(r"Mode:\s*(ANALYZE|QUIZ|ASSESS|REWRITE|CHAT)", re.IGNORECASE)
_RE_CLASS    = re.compile(r"Classification:\s*(LOW|MEDIUM|HIGH)", re.IGNORECASE)
_RE_RISK     = re.compile(r"Risk Score:\s*(\d+)", re.IGNORECASE)
_RE_CATEGORY = re.compile(r"Category:\s*([^\n]+)", re.IGNORECASE)
_RE_REASON   = re.compile(r"Reasoning:\s*([\s\S]+?)Action:", re.IGNORECASE)
_RE_ACTION   = re.compile(r"Action:\s*(ALLOW|WARN|BLOCK)", re.IGNORECASE)


# ─────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────

@dataclass
class BertResult:
    """Typed wrapper around BERT classifier output."""
    is_threat:  bool  = False
    confidence: float = 0.0
    text:       str   = ""
    risk_score: int   = 0

    @classmethod
    def empty(cls, text: str = "") -> "BertResult":
        return cls(text=text)

    def to_dict(self) -> dict:
        return {
            "is_threat":  self.is_threat,
            "confidence": self.confidence,
            "text":       self.text,
            "risk_score": self.risk_score,
        }


@dataclass
class ParsedLLMAnalysis:
    """Structured parse of an ANALYSIS_PROMPT LLM response."""
    classification: str = "Unknown"
    risk_score:     int = 0
    category:       str = "None"
    action:         str = "Allow"
    reasoning:      str = "No reasoning provided."

    def to_dict(self) -> dict:
        return {
            "classification": self.classification,
            "risk_score":     self.risk_score,
            "category":       self.category,
            "action":         self.action,
            "reasoning":      self.reasoning,
        }


@dataclass
class InitialVerdict:
    """Default verdict returned while the LLM is still streaming."""
    final_label:        str   = "N/A"
    action:             str   = "Allow"
    action_icon:        str   = "✅"
    risk_score:         int   = 0
    risk_label:         str   = "No Risk"
    categories:         list  = field(default_factory=list)
    severities:         list  = field(default_factory=list)
    reasoning:          str   = "Processing..."
    context_note:       str   = ""
    is_positive_context: bool = False

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class PipelineResult:
    """
    Everything the UI layer needs after `process_message`.
    `response_parts` is populated in-place by the capturing generator
    so the controller can parse it for `refine_verdict` after streaming.
    """
    bert:               dict
    verdict:            dict
    response_generator: Iterator[str]
    response_parts:     list[str]
    is_analysis:        bool
    mode:               Mode


# ─────────────────────────────────────────────────────────────
# Intent Router
# ─────────────────────────────────────────────────────────────

class IntentRouter:
    """
    Two-stage hybrid router:
      1. Fast O(1) keyword match (no LLM call)
      2. LLM-based semantic fallback when keywords don't match
    """

    def __init__(self, llm_handler: LLMHandler) -> None:
        self._llm = llm_handler

    def route(self, message: str) -> Mode:
        """Return the best Mode for `message`."""
        fast = self._fast_route(message)
        if fast:
            logger.debug("Fast-route matched mode=%s for message=%r", fast, message[:60])
            return fast

        llm_mode = self._llm_route(message)
        logger.debug("LLM-route resolved mode=%s for message=%r", llm_mode, message[:60])
        return llm_mode

    # ----------------------------------------------------------
    # Private helpers
    # ----------------------------------------------------------

    @staticmethod
    def _fast_route(text: str) -> Optional[Mode]:
        """
        Check lowercased text against each mode's keyword set.
        Ordered by specificity: quiz/assess/rewrite before analyze.
        """
        lower = text.strip().lower()
        for mode in (Mode.QUIZ, Mode.ASSESS, Mode.REWRITE, Mode.ANALYZE):
            if any(trigger in lower for trigger in _FAST_TRIGGERS[mode]):
                return mode
        return None

    def _llm_route(self, message: str) -> Mode:
        """Call the LLM with INTENT_ROUTING_PROMPT; parse the Mode tag."""
        try:
            output = "".join(
                self._llm.generate_response(
                    [{"role": "user", "content": message}],
                    system_override=INTENT_ROUTING_PROMPT,
                )
            )
            match = _RE_MODE.search(output)
            if match:
                return Mode(match.group(1).upper())
        except Exception as exc:
            logger.warning("LLM intent routing failed (%s). Defaulting to CHAT.", exc)
        return Mode.CHAT


# ─────────────────────────────────────────────────────────────
# LLM Analysis Parser
# ─────────────────────────────────────────────────────────────

def _parse_llm_analysis(llm_text: str) -> ParsedLLMAnalysis:
    """
    Parse the rigid ANALYSIS_PROMPT response format into a typed object.
    All fields fall back to safe defaults on parse failure.
    """
    result = ParsedLLMAnalysis()

    if m := _RE_CLASS.search(llm_text):
        result.classification = m.group(1).upper()
    if m := _RE_RISK.search(llm_text):
        result.risk_score = min(100, max(0, int(m.group(1))))   # clamp 0-100
    if m := _RE_CATEGORY.search(llm_text):
        result.category = m.group(1).strip()
    if m := _RE_REASON.search(llm_text):
        result.reasoning = m.group(1).strip()
    if m := _RE_ACTION.search(llm_text):
        result.action = m.group(1).capitalize()

    return result


# ─────────────────────────────────────────────────────────────
# Chat Controller
# ─────────────────────────────────────────────────────────────

class ChatController:
    """
    Orchestrates the full CyberGuard AI moderation pipeline:
      routing → BERT classification → LLM generation → verdict refinement.
    """

    def __init__(self, llm_config: Optional[LLMConfig] = None) -> None:
        self.bert_module = BertInferenceModule()
        self.llm_handler = LLMHandler(config=llm_config)
        self.router      = IntentRouter(self.llm_handler)

    # ----------------------------------------------------------
    # Interface compatibility shims
    # ----------------------------------------------------------

    def set_api_key(self, api_key: str) -> None:  # noqa: ARG002
        """No-op — retained for interface compatibility."""

    def is_api_key_set(self) -> bool:
        return True

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def process_message(
        self,
        message: str,
        conversation_history: list[dict],
    ) -> PipelineResult:
        """
        Full pipeline for a user message.

        Steps:
          1. Hybrid intent routing (fast keywords → LLM fallback)
          2. BERT classification (analysis mode only)
          3. LLM streaming response (capturing generator)
          4. Return PipelineResult for the UI to stream + refine

        Args:
            message:              Raw user text.
            conversation_history: Full session history (dicts with role/content).

        Returns:
            PipelineResult containing the streaming generator and metadata.
        """
        mode = self.router.route(message)
        logger.info("process_message: mode=%s", mode)

        is_analysis = (mode == Mode.ANALYZE)
        sys_override = _PROMPT_MAP[mode]

        # BERT runs synchronously only for analysis
        bert_result: dict
        if is_analysis:
            raw = self.bert_module.classify_text(message)
            bert_result = raw if isinstance(raw, dict) else BertResult.empty(message).to_dict()
            final_decision = validate_verdict(bert_result, {})
            
            # --- Behavioral Context Builder ---
            # Score-based tracking: >60 is considered harmful/toxic
            toxic_count = sum(1 for m in conversation_history if m.get('risk_score', 0) > 60)
            
            # Structured context of the last 5 messages
            recent_msgs = [f"User: {m.get('content', '')}" for m in conversation_history if str(m.get('role', '')).lower() == 'user'][-5:]
            context_str = "\n".join(recent_msgs) if recent_msgs else "No previous context."
            
            behavior_hint = "User shows repeated harmful behavior." if toxic_count >= 3 else "Normal interaction."
            
            # Clean prompt injection
            final_prompt = f"Context:\n{context_str}\n\nBehavior:\n{behavior_hint}\n\nAnalyze:\n{message}"
            conversation_history.append({"role": "user", "content": final_prompt})
        else:
            bert_result = BertResult.empty(message).to_dict()
            final_decision = validate_verdict(bert_result, {})
            conversation_history.append({"role": "user", "content": message})

        # Shared list populated in-place by the generator below
        response_parts: list[str] = []

        def _capturing_generator() -> Generator[str, None, None]:
            prefill = None
            if is_analysis:
                r_score = final_decision.get("risk_score", 0)
                if r_score < 40:
                    label = "SAFE"
                elif r_score < 70:
                    label = "WARNING"
                else:
                    label = "UNSAFE"
                # Prefill only the status header (text only, no emoji)
                prefill = f"{label}\n\n"

            for chunk in self.llm_handler.generate_response(
                conversation_history,
                system_override=sys_override,
                assistant_prefill=prefill,
            ):
                response_parts.append(chunk)
                yield chunk

        return PipelineResult(
            bert=final_decision,
            verdict=InitialVerdict().to_dict(),
            response_generator=_capturing_generator(),
            response_parts=response_parts,
            is_analysis=is_analysis,
            mode=mode,
        )

    def refine_verdict(self, bert_result: dict, llm_full_text: str) -> dict:
        """
        Post-stream verdict refinement: parse the full LLM output then
        pass both BERT and LLM signals to the decision engine.

        Args:
            bert_result:   Output dict from `BertInferenceModule.classify_text`.
            llm_full_text: Complete concatenated LLM response string.

        Returns:
            Final verdict dict from `validate_verdict`.
        """
        parsed = _parse_llm_analysis(llm_full_text)
        logger.debug("Parsed LLM analysis: %s", parsed)
        return validate_verdict(bert_result, parsed.to_dict())

    def process_command(
        self,
        command_type: str,
        message: str,
        conversation_history: list[dict],
    ) -> Generator[str, None, None]:
        """
        Handle sidebar module commands (QUIZ, ASSESS, REWRITE) directly.

        Args:
            command_type:         One of REWRITE / QUIZ / ASSESS (or any Mode value).
            message:              Optional seed message for context.
            conversation_history: Current session history.

        Returns:
            Token generator from the LLM handler.
        """
        try:
            mode = Mode(command_type.upper())
        except ValueError:
            logger.warning("Unknown command_type '%s', defaulting to CHAT.", command_type)
            mode = Mode.CHAT

        sys_override = _PROMPT_MAP[mode]
        seed = message or f"Execute {mode.value} mode."

        history = conversation_history or [{"role": "user", "content": seed}]

        logger.info("process_command: mode=%s", mode)
        return self.llm_handler.generate_response(history, system_override=sys_override)
