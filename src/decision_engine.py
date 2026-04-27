import re

CATEGORY_PATTERNS = {
    "Threat": [r"\bkill\b", r"\bhurt\b", r"\bbeat\b", r"\bshoot\b", r"\bdead\b"],
    "Hate Speech": [r"\b(racial|racist|slur|bigot|nazi)\b", r"\b(n-word)\b"],
    "Harassment": [r"\bstop existing\b", r"\bleave\b", r"\bblock(ed)?\b"],
    "Insult": [r"\b(stupid|dumb|idiot|loser|ugly|trash|bitch|ass)\b", r"\byou (are|r|suck)\b"],
    "Profanity": [r"\b(fuck|shit|bitch|asshole|damn)\b", r"\bwtf\b", r"\bstfu\b"],
    "Spam": [r"\b(click here|buy now|free money)\b", r"http[s]?://\S+.*http[s]?://"]
}

def scan_text(text: str) -> list[str]:
    text_lower = text.lower()
    detected = []
    for cat, patterns in CATEGORY_PATTERNS.items():
        if any(re.search(p, text_lower) for p in patterns):
            detected.append(cat)
    return detected

def validate_verdict(bert_result: dict, parsed_llm: dict) -> dict:
    """
    Validates the LLM's classification output.
    Applies guardrails to prevent hallucination over-blocking or under-blocking.
    """
    text = bert_result.get("text", "")
    bert_confidence = bert_result.get("confidence", 0.0)
    bert_is_threat = bert_result.get("is_threat", False)

    llm_classification = parsed_llm.get("classification", "Unknown") # HIGH, MEDIUM, LOW
    llm_risk = parsed_llm.get("risk_score", 0)
    llm_category = parsed_llm.get("category", "None")
    llm_action = parsed_llm.get("action", "Allow")
    llm_reasoning = parsed_llm.get("reasoning", "")

    # Rule-based scan
    found_categories = scan_text(text)
    has_toxic_words = len(found_categories) > 0

    # Guardrail 1: If LLM says HIGH risk but 0 toxic words AND BERT confidence is low 
    # -> Downgrade to WARN / Medium risk (Prevent False Positive)
    if llm_classification == "HIGH" and not has_toxic_words and not bert_is_threat:
        if llm_risk > 60: llm_risk = 60
        llm_classification = "MEDIUM"
        llm_action = "Warn"
        llm_reasoning = llm_reasoning + "\n[Validator Guardrail: Suppressed due to lack of hard keywords]"

    # Guardrail 2: If LLM completely failed to parse, use BERT
    if llm_classification == "Unknown":
        if bert_is_threat:
            llm_classification = "HIGH" if bert_confidence > 0.8 else "MEDIUM"
            llm_risk = int(bert_confidence * 100)
            llm_action = "Block" if bert_confidence > 0.8 else "Warn"
            llm_category = "Suspected Toxicity"
            llm_reasoning = "LLM parsing failed. Fast-path BERT classifier enacted."
        else:
            llm_classification = "LOW"
            llm_risk = 0
            llm_action = "Allow"
            llm_category = "None"
            llm_reasoning = "LLM parsing failed. Fast-path BERT verified safe."

    # Mapping to UI expected fields
    final_label = "Safe"
    if llm_classification == "HIGH": final_label = "Unsafe"
    elif llm_classification == "MEDIUM": final_label = "Needs Review"

    # Merge categories
    cats = list(dict.fromkeys([llm_category] + found_categories))
    if "None" in cats and len(cats) > 1:
        cats.remove("None")
    if "Other" in cats and len(cats) > 1:
        cats.remove("Other")
    if not cats: cats = ["None"]

    risk_label = "High Risk" if llm_risk >= 70 else "Medium Risk" if llm_risk >= 40 else "Low Risk"
    action_icon = "🚫" if llm_action == "Block" else "⚠️" if llm_action == "Warn" else "✅"

    return {
        "final_label": final_label,
        "action": llm_action,
        "action_icon": action_icon,
        "risk_score": llm_risk,
        "risk_label": risk_label,
        "categories": cats,
        "severities": [llm_classification],
        "reasoning": llm_reasoning,
        "context_note": "Rule validated.",
        "is_positive_context": False,
    }
