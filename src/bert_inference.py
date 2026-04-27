import os
import sys
import re

# Add parent directory to path to import the original predict_final module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from predict_final import predict_text
except ImportError as e:
    print(f"Error importing predict_final: {e}")
    # Fallback mock for testing if predict_final is inaccessible
    def predict_text(text):
        if any(w in text.lower() for w in ["hate", "dumb", "idiot", "kill", "stupid", "ugly"]):
            return "CYBERBULLYING", 0.95
        return "SAFE", 0.98


# ── Positive context patterns (context-awareness) ───────────────────────────
_POSITIVE_CONTEXT = [
    r"\b(killing it|slaying|crushing it|on fire|beast mode)\b",
    r"\b(you.re amazing|well done|great job|proud of you)\b",
    r"\b(go kill it|kill it out there)\b",
]


def _is_positive_context(text: str) -> bool:
    """Return True if text uses positive slang that looks dangerous out of context."""
    t = text.lower()
    return any(re.search(p, t) for p in _POSITIVE_CONTEXT)


class BertInferenceModule:
    """
    Wrapper class around the original PyTorch BERT classifier.
    Ensures modularity if we later decide to swap the backend.
    Adds: risk_score, context awareness, category hints.
    """

    @staticmethod
    def classify_text(text: str) -> dict:
        """
        Runs the text through the BERT model.
        Returns a dictionary with structured output including risk_score.
        """
        positive_ctx = _is_positive_context(text)

        try:
            label, confidence = predict_text(text)

            # If BERT says threat but context is clearly positive → downgrade
            if label == "CYBERBULLYING" and positive_ctx:
                label = "SAFE"
                confidence = max(0.0, confidence - 0.4)

            is_threat = label == "CYBERBULLYING"

            # Compute a preliminary risk score from BERT alone (0-100)
            if is_threat:
                risk_score = int(confidence * 90)      # cap at 90 — LLM will refine
            else:
                # For safe content, confidence represents safety certainty
                # Display as a positive confidence percentage
                risk_score = 0  # Safe content has 0 risk
                confidence = confidence  # Keep actual confidence for display

            return {
                "text": text,
                "label": label,
                "confidence": round(confidence, 4),
                "is_threat": is_threat,
                "risk_score": risk_score,
                "positive_context": positive_ctx,
            }

        except Exception as e:
            import traceback
            error_msg = str(e)
            # Return safe default with medium confidence (0.5) instead of 0.0
            return {
                "text": text,
                "label": "SAFE",
                "confidence": 0.5,  # Neutral confidence when model fails
                "is_threat": False,
                "risk_score": 0,
                "positive_context": False,
                "error": error_msg,
                "traceback": traceback.format_exc(),
            }
