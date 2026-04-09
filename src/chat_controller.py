from src.bert_inference import BertInferenceModule
from src.llm_handler import LLMHandler
from src.prompt_templates import (
    EXPLANATION_PROMPT, SAFE_RESPONSE_PROMPT, REWRITE_PROMPT,
    QUIZ_PROMPT, ASSESSMENT_PROMPT, SYSTEM_PROMPT, NOT_ANALYSIS_REPLY
)

# ── Keywords that signal an explicit analysis request ─────────────────────────
ANALYSIS_TRIGGERS = {
    # Primary action words
    "analyze", "analyse", "analysis", "classify", "detect", "identify",
    "evaluate", "review", "inspect", "examine", "moderate", "flag", "rate",
    # Moderation context words (only meaningful when paired with intent)
    "toxicity", "abusive", "hate speech", "profanity", "slur",
    # Explicit phrases
    "check this", "check this text", "is this toxic", "is this cyberbullying",
    "is this safe", "is this harmful", "is this offensive", "is this abusive",
    "is this rude", "is this inappropriate", "how harmful", "does this contain",
    "detect toxicity", "rate this message", "flag this message",
    "moderate this", "classify this",
}

# ── Prefixes that indicate an explanatory question, NOT an analysis request ───
EXPLANATION_PREFIXES = (
    "what is", "what are", "define", "explain", "how does", "how do",
    "tell me about", "describe", "meaning of", "what does", "can you explain",
    "what's", "whats",
)


def _is_analysis_request(text: str) -> bool:
    """
    Return True only when the user clearly wants text analyzed.
    Explanatory questions (e.g. 'what is cyberbullying?') stay in chat mode
    even if they contain moderation keywords.
    """
    lower = text.strip().lower()

    # Rule 1: If it starts with an explanation prefix → chat mode
    if any(lower.startswith(prefix) for prefix in EXPLANATION_PREFIXES):
        return False

    # Rule 2: If it contains a clear analysis trigger → analysis mode
    return any(trigger in lower for trigger in ANALYSIS_TRIGGERS)


def _instant_generator(text: str):
    """Yield a static reply as a generator (to match the streaming interface)."""
    yield text


class ChatController:
    def __init__(self):
        self.bert_module = BertInferenceModule()
        self.llm_handler = LLMHandler()
        
    def set_api_key(self, api_key):
        pass  # Unused for local Ollama

    def is_api_key_set(self):
        return True  # Always true for local Ollama usage

    def process_message(self, message, conversation_history):
        # ── Step 1: Intent Detection ──────────────────────────────────────
        if not _is_analysis_request(message):
            # CHAT MODE: pass to LLM with only the base SYSTEM_PROMPT
            # so it responds naturally and conversationally.
            resp_gen = self.llm_handler.generate_response(
                conversation_history, system_override=SYSTEM_PROMPT
            )
            return {
                "bert": {"is_threat": False, "confidence": 0.0, "text": message},
                "response_generator": resp_gen
            }

        # ── Step 2: BERT Classification ───────────────────────────────────
        bert_result = self.bert_module.classify_text(message)

        # ── Step 3: Route prompts based on BERT result ────────────────────
        if bert_result["is_threat"]:
            sys_override = SYSTEM_PROMPT + "\n\n" + EXPLANATION_PROMPT
        else:
            sys_override = SYSTEM_PROMPT + "\n\n" + SAFE_RESPONSE_PROMPT

        # ── Step 4: LLM Generation ────────────────────────────────────────
        resp_gen = self.llm_handler.generate_response(
            conversation_history, system_override=sys_override
        )

        return {
            "bert": bert_result,
            "response_generator": resp_gen
        }

    def process_command(self, command_type, message, conversation_history):
        sys_override = SYSTEM_PROMPT

        # Inject a hidden logic prompt so the LLM generates structured output immediately
        fake_user_prompt = ""

        if command_type == "REWRITE":
            sys_override += "\n\n" + REWRITE_PROMPT
        elif command_type == "QUIZ":
            sys_override += "\n\n" + QUIZ_PROMPT
            fake_user_prompt = (
                f"Generate a mixed difficulty cyberbullying detection and content moderation quiz "
                f"right now. Random Entropy Seed: {message}. Output ONLY JSON."
            )
        elif command_type == "ASSESS":
            sys_override += "\n\n" + ASSESSMENT_PROMPT
            fake_user_prompt = (
                f"Generate a mixed difficulty cyberbullying moderation scenario assessment paragraph "
                f"right now. Random Entropy Seed: {message}. Output ONLY JSON."
            )

        if not conversation_history and fake_user_prompt:
            conversation_history = [{"role": "user", "content": fake_user_prompt}]

        return self.llm_handler.generate_response(
            conversation_history, system_override=sys_override
        )

