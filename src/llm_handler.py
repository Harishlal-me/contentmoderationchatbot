"""
llm_handler.py — Enhanced CyberGuard AI LLM Handler
-----------------------------------------------------
Improvements:
  - Dataclass-based message models for type safety
  - Enum-driven intent detection (no magic strings)
  - Configurable settings via LLMConfig dataclass
  - Retry logic with exponential back-off
  - Structured logging instead of bare print()
  - Streaming helper refactored into its own method
  - Fallback logic fully decoupled from HTTP logic
  - Comprehensive docstrings and inline comments
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Generator, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from src.prompt_templates import CHAT_PROMPT
except ImportError:  # graceful degradation if module is missing
    CHAT_PROMPT = "You are CyberGuard AI, an assistant for cyberbullying awareness."

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)


# ─────────────────────────────────────────────────────────────
# Constants & Enums
# ─────────────────────────────────────────────────────────────

GREETING_WORDS: frozenset[str] = frozenset({
    "hi", "hello", "hey", "hiya", "howdy", "sup", "yo",
    "greetings", "good morning", "good afternoon", "good evening",
})

POSITIVE_WORDS: tuple[str, ...] = ("thank", "thanks", "thx", "great", "awesome", "cool", "nice")

ANALYSIS_WORDS: tuple[str, ...] = (
    "analyze", "analysis", "check", "detect",
    "is this", "is it", "cyberbully", "toxic", "harmful", "safe",
)


class UserIntent(Enum):
    """Categorised user intentions for smart fallback selection."""
    GREETING   = auto()
    QUIZ       = auto()
    ASSESSMENT = auto()
    POSITIVE   = auto()
    ANALYSIS   = auto()
    UNKNOWN    = auto()


# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

@dataclass
class LLMConfig:
    """
    Central configuration for the LLM handler.

    Attributes:
        model:          Ollama model tag to use.
        base_url:       Base URL of the Ollama server.
        timeout:        HTTP request timeout in seconds.
        max_retries:    Number of automatic retries on transient failures.
        context_window: How many history turns to include per request.
        num_ctx:        LLM context size (tokens).
        num_predict:    Max tokens to generate.
        stream_delay:   Seconds between words in fallback streaming.
    """
    model:          str   = "llama3.2"
    base_url:       str   = "http://localhost:11434"
    timeout:        int   = 60
    max_retries:    int   = 2
    context_window: int   = 10
    num_ctx:        int   = 2048
    num_predict:    int   = 1024
    stream_delay:   float = 0.03

    @property
    def chat_url(self) -> str:
        return f"{self.base_url}/api/chat"


# ─────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────

@dataclass
class Message:
    """Represents a single conversation turn."""
    role:    str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            role=str(data.get("role", "user")),
            content=str(data.get("content", "")),
        )


@dataclass
class ConversationContext:
    """
    Wraps a raw history list and exposes helpers for intent detection
    and building the message payload for the API.
    """
    history: list[dict] = field(default_factory=list)

    @property
    def last_user_message(self) -> str:
        for msg in reversed(self.history):
            if msg.get("role") == "user":
                return msg.get("content", "").strip().lower()
        return ""

    def as_messages(self, window: int) -> list[dict[str, str]]:
        """Return the last `window` turns as API-ready dicts."""
        return [Message.from_dict(m).to_dict() for m in self.history[-window:]]

    def detect_intent(self, system_override: Optional[str]) -> UserIntent:
        """
        Determine the user's primary intent from the last message
        and the active system prompt, so the right fallback fires.
        """
        msg  = self.last_user_message
        sys  = system_override or ""
        word = msg.split()[0] if msg.split() else ""

        # Greeting
        if word in GREETING_WORDS or msg in GREETING_WORDS:
            return UserIntent.GREETING

        # Quiz — triggered by keyword in system prompt OR user message
        quiz_signals = ("QUIZ_PROMPT", "Quiz Generator", "Difficulty Level",
                        "interactive Multiple-Choice Quiz")
        if "quiz" in msg or any(s in sys for s in quiz_signals):
            return UserIntent.QUIZ

        # Assessment
        assess_signals = ("ASSESSMENT_PROMPT", "Assessment Module", "moderation training")
        if "assessment" in msg or any(s in sys for s in assess_signals):
            return UserIntent.ASSESSMENT

        # Positive sentiment
        if any(w in msg for w in POSITIVE_WORDS):
            return UserIntent.POSITIVE

        # Analysis request
        if any(w in msg for w in ANALYSIS_WORDS):
            return UserIntent.ANALYSIS

        return UserIntent.UNKNOWN


# ─────────────────────────────────────────────────────────────
# Fallback Response Builder
# ─────────────────────────────────────────────────────────────

class FallbackResponder:
    """
    Generates context-aware fallback responses when the LLM is offline.
    Each intent maps to a dedicated builder method for easy extension.
    """

    _RESPONSES: dict[UserIntent, str] = {
        UserIntent.GREETING: (
            "👋 Hey there! I'm **CyberGuard AI** — nice to meet you! "
            "I'm here to help with online safety, cyberbullying awareness, and content moderation.\n\n"
            "Feel free to just chat, ask me anything, or if you'd like I can:\n"
            "- 🔍 **Analyze text** for toxicity\n"
            "- 🎯 **Run a quiz** on cyberbullying detection\n"
            "- 📊 **Start an assessment** exercise\n"
            "- ✍️ **Rewrite** harmful text into something safer\n\n"
            "What's on your mind?"
        ),
        UserIntent.QUIZ: (
            "🎯 **Let's start the Cyberbullying Detection Quiz!**\n\n"
            "Before I generate your questions, I need two things from you:\n\n"
            "**1. Difficulty Level:**\n"
            "- 🟢 **Easy** — Basic recognition of obvious bullying\n"
            "- 🟡 **Medium** — Nuanced cases including indirect abuse\n"
            "- 🔴 **Hard** — Complex scenarios, severity classification\n\n"
            "**2. Topic:**\n"
            "- Direct Insults\n"
            "- Indirect / Subtle Abuse\n"
            "- Online Harassment\n"
            "- Severity Classification\n"
            "- All Topics (mixed)\n\n"
            "Reply with your choices and I'll generate your personalised quiz! 🚀"
        ),
        UserIntent.ASSESSMENT: (
            "📊 **Content Moderation Assessment — Starting Now!**\n\n"
            "Read the following paragraph carefully. It contains a **mix of normal and harmful sentences**.\n\n"
            "---\n\n"
            "1. The weather today is really nice and perfect for a walk.\n"
            "2. I genuinely enjoy collaborating with everyone on this project.\n"
            "3. People like you were never meant to be part of this group.\n"
            "4. Can we schedule a meeting to discuss the new features?\n"
            "5. Nobody wants to hear what you have to say — just stay silent.\n"
            "6. Great work on the presentation, everyone was impressed!\n\n"
            "---\n\n"
            "**Your task:**\n"
            "1. **Identify** which sentence numbers are harmful\n"
            "2. **Assign severity** to each: `Low` / `Medium` / `High`\n\n"
            "Take your time and share your answers when ready! 💪"
        ),
        UserIntent.POSITIVE: (
            "😊 You're welcome! Is there anything else I can help you with?\n\n"
            "I can **analyze text**, run a **quiz**, or start an **assessment** anytime."
        ),
        UserIntent.ANALYSIS: (
            "🔍 **Analysis Mode**\n\n"
            "I can analyze that for you! My BERT classifier has already processed your message.\n\n"
            "Once my language model (Ollama) finishes loading, I'll provide:\n"
            "- **Classification** — What type of content this is\n"
            "- **Severity** — Low / Medium / High\n"
            "- **Reasoning** — Why it's harmful or safe\n"
            "- **Alternatives** — Safer ways to express the same idea\n\n"
            "Please share the text you'd like me to analyze and I'll get started!"
        ),
        UserIntent.UNKNOWN: (
            "I'm here and happy to chat! 😊 "
            "I specialize in online safety and cyberbullying awareness, but feel free to ask me anything.\n\n"
            "If you'd like, I can analyze text for toxicity, run a cyberbullying quiz, "
            "start a practice assessment, or just have a conversation!"
        ),
    }

    @classmethod
    def get(cls, intent: UserIntent) -> str:
        """Return the pre-written fallback string for the given intent."""
        return cls._RESPONSES.get(intent, cls._RESPONSES[UserIntent.UNKNOWN])


# ─────────────────────────────────────────────────────────────
# LLM Handler
# ─────────────────────────────────────────────────────────────

class LLMHandler:
    """
    Manages communication with the local Ollama LLM server.

    Features:
    - Streaming token-by-token responses
    - Configurable retry + back-off via `requests.Session`
    - Context-aware fallback when the server is unreachable
    - Clean separation of config, context, and fallback concerns
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        self.config  = config or LLMConfig()
        self.session = self._build_session()

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def set_model(self, model: str) -> None:
        """Hot-swap the model without re-creating the handler."""
        self.config.model = model
        logger.info("Model updated to '%s'", model)

    # Kept for backwards compatibility with existing callers
    def set_api_key(self, api_key: str) -> None:  # noqa: ARG002
        """No-op — Ollama does not require an API key."""

    def generate_response(
        self,
        conversation_history: list[dict],
        system_override: Optional[str] = None,
        assistant_prefill: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """
        Yield response tokens from the Ollama LLM.

        If the server is unreachable or returns an error, automatically
        falls back to a context-aware canned response streamed word-by-word.

        Args:
            conversation_history: List of ``{"role": …, "content": …}`` dicts.
            system_override:      Optional system prompt to replace the default.
            assistant_prefill:    Optional string prepended to the assistant turn.

        Yields:
            Strings (tokens or words) that form the complete response.
        """
        ctx     = ConversationContext(history=conversation_history)
        payload = self._build_payload(ctx, system_override, assistant_prefill)

        try:
            yield from self._stream_llm(payload, assistant_prefill)
        except Exception as exc:
            logger.warning("LLM unavailable (%s). Serving fallback response.", exc)
            intent = ctx.detect_intent(system_override)
            yield from self._stream_fallback(FallbackResponder.get(intent))

    # ----------------------------------------------------------
    # Private helpers
    # ----------------------------------------------------------

    def _build_session(self) -> requests.Session:
        """
        Create a `requests.Session` with automatic retry on 5xx errors
        and connection failures, using exponential back-off.
        """
        retry = Retry(
            total=self.config.max_retries,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods={"POST"},
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _build_payload(
        self,
        ctx: ConversationContext,
        system_override: Optional[str],
        assistant_prefill: Optional[str],
    ) -> dict:
        """Assemble the JSON payload for the Ollama /api/chat endpoint."""
        system_prompt = system_override or CHAT_PROMPT
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        messages.extend(ctx.as_messages(self.config.context_window))

        if assistant_prefill:
            messages.append({"role": "assistant", "content": assistant_prefill})

        return {
            "model":    self.config.model,
            "messages": messages,
            "stream":   True,
            "options": {
                "num_ctx":     self.config.num_ctx,
                "num_predict": self.config.num_predict,
            },
        }

    def _stream_llm(
        self,
        payload: dict,
        assistant_prefill: Optional[str],
    ) -> Generator[str, None, None]:
        """
        POST the payload to Ollama and yield content tokens as they arrive.

        Raises:
            requests.HTTPError: If the server responds with a 4xx / 5xx status.
            requests.ConnectionError: If the server cannot be reached.
        """
        if assistant_prefill:
            yield assistant_prefill

        with self.session.post(
            self.config.chat_url,
            json=payload,
            stream=True,
            timeout=self.config.timeout,
        ) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines():
                if not raw_line:
                    continue
                try:
                    data = json.loads(raw_line.decode("utf-8"))
                except json.JSONDecodeError:
                    logger.debug("Skipping non-JSON line: %r", raw_line)
                    continue

                token = data.get("message", {}).get("content")
                if token:
                    yield token

                if data.get("done"):
                    logger.debug(
                        "LLM stream complete. eval_duration=%s ms",
                        data.get("eval_duration", "n/a"),
                    )
                    break

    def _stream_fallback(self, text: str) -> Generator[str, None, None]:
        """
        Stream a fallback string word-by-word to simulate a typing effect.

        Args:
            text: The complete fallback response string.

        Yields:
            Individual words followed by a space (except the last).
        """
        words = text.split(" ")
        last  = len(words) - 1
        for idx, word in enumerate(words):
            time.sleep(self.config.stream_delay)
            yield word if idx == last else word + " "
