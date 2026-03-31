"""
Simple Prediction Script
Test your trained model on custom texts
"""

import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer
import sys
import os

# Add models directory to Python path so torch.load can find config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))


class BERTClassifier(nn.Module):
    """BERT model for classification"""
    def __init__(self, model_name='bert-base-uncased', num_classes=2, dropout=0.3):
        super(BERTClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits


def load_model(model_path, device):
    """Load trained model"""
    print("Loading model...")
    
    # Create model
    model = BERTClassifier(
        model_name='bert-base-uncased',
        num_classes=2,
        dropout=0.3
    )
    
    # Load weights
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
        acc = checkpoint.get('best_val_accuracy', 'N/A')
        print(f"  Best validation accuracy: {acc}")
    else:
        model.load_state_dict(checkpoint)
        
    model.to(device)
    model.eval()
    
    print("✓ Model loaded")
    
    return model


def predict_texts(model, tokenizer, texts, device):
    """
    Predict cyberbullying for list of texts
    
    Args:
        model: Trained model
        tokenizer: BERT tokenizer
        texts: List of text strings
        device: Device to run on
    """
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    for i, text in enumerate(texts, 1):
        # Tokenize
        encoding = tokenizer(
            text,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        # Move to device
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        # Predict
        with torch.no_grad():
            logits = model(input_ids, attention_mask)
            probabilities = torch.softmax(logits, dim=1)
            prediction = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][prediction].item()
        
        # Display result
        label = "🚨 CYBERBULLYING" if prediction == 1 else "✅ NOT CYBERBULLYING"
        
        print(f"\n[{i}] Text: '{text}'")
        print(f"    Prediction: {label}")
        print(f"    Confidence: {confidence*100:.1f}%")
        print(f"    Probabilities: Not CB={probabilities[0][0].item()*100:.1f}% | CB={probabilities[0][1].item()*100:.1f}%")
    
    print("\n" + "="*70)


# Global variables for caching
GLOBAL_MODEL = None
GLOBAL_TOKENIZER = None

def get_model_and_tokenizer(device=None):
    """Load model and tokenizer once and cache them globally."""
    global GLOBAL_MODEL, GLOBAL_TOKENIZER
    
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    if GLOBAL_MODEL is None:
        model_path = os.path.join(os.path.dirname(__file__), 'models/saved_models/bert_cyberbullying_model.pth')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
        GLOBAL_MODEL = load_model(model_path, device)
        
    if GLOBAL_TOKENIZER is None:
        GLOBAL_TOKENIZER = BertTokenizer.from_pretrained('bert-base-uncased')
        
    return GLOBAL_MODEL, GLOBAL_TOKENIZER, device

def predict_text(text):
    """
    Predict cyberbullying for a single text.
    Returns:
        tuple: (label: str, confidence: float)
        label is either 'SAFE' or 'CYBERBULLYING'
    """
    model, tokenizer, device = get_model_and_tokenizer()
    
    encoding = tokenizer(
        text,
        add_special_tokens=True,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    )
    
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    
    with torch.no_grad():
        logits = model(input_ids, attention_mask)
        probabilities = torch.softmax(logits, dim=1)
        
        # Use lower threshold for cyberbullying due to imbalanced dataset
        prob_cb = probabilities[0][1].item()
        prediction = 1 if prob_cb >= 0.45 else 0
        confidence = prob_cb if prediction == 1 else probabilities[0][0].item()
        
    label = "CYBERBULLYING" if prediction == 1 else "SAFE"
    
    return label, confidence

def main():
    """Test the newly created specific pipeline."""
    print("Testing backend prediction pipeline...")
    tests = [
        "You are amazing",
        "Go kill yourself",
        "You look stupid"
    ]
    for t in tests:
        label, conf = predict_text(t)
        print(f"Text: '{t}' -> Label: {label}, Confidence: {conf*100:.2f}%")
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[Error]: {str(e)}")
        import traceback
        traceback.print_exc()
