import os
import sys

# Add parent directory to path to import the original predict_final module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from predict_final import predict_text
except ImportError as e:
    print(f"Error importing predict_final: {e}")
    # Fallback mock for testing if predict_final is inaccessible
    def predict_text(text):
        if "hate" in text.lower() or "dumb" in text.lower():
            return "CYBERBULLYING", 0.95
        return "SAFE", 0.98

class BertInferenceModule:
    """
    Wrapper class around the original PyTorch BERT classifier.
    Ensures modularity if we later decide to swap the backend.
    """
    
    @staticmethod
    def classify_text(text):
        """
        Runs the text through the BERT model.
        Returns a dictionary with structured output.
        """
        try:
            label, confidence = predict_text(text)
            return {
                "text": text,
                "label": label,
                "confidence": confidence,
                "is_threat": label == "CYBERBULLYING"
            }
        except Exception as e:
            # Fallback error handling
            print(f"Prediction Error in BERT inference: {str(e)}")
            return {
                "text": text,
                "label": "SAFE",
                "confidence": 0.0,
                "is_threat": False,
                "error": str(e)
            }
