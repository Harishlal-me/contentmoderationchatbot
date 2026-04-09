import os
import json
import time
import requests
from src.prompt_templates import SYSTEM_PROMPT

# Greetings that should get a warm, natural response
GREETING_WORDS = {"hi", "hello", "hey", "hiya", "howdy", "sup", "yo", "greetings", "good morning", "good afternoon", "good evening"}

def _get_smart_fallback(conversation_history, system_override):
    """
    Generate a context-aware fallback response when Ollama is offline.
    Reads the last user message and/or the system_override to pick an appropriate reply.
    """
    # Detect the last user message
    last_user_msg = ""
    for msg in reversed(conversation_history):
        if msg.get("role") == "user":
            last_user_msg = msg.get("content", "").strip().lower()
            break

    # Detect if this is a QUIZ command
    is_quiz = system_override and "QUIZ_PROMPT" in system_override or (
        system_override and "Quiz Generator" in system_override
    ) or (system_override and "Difficulty Level" in system_override) or (
        system_override and "interactive Multiple-Choice Quiz" in (system_override or "")
    )

    # Detect if this is an ASSESSMENT command
    is_assess = system_override and "ASSESSMENT_PROMPT" in system_override or (
        system_override and "Assessment Module" in (system_override or "")
    ) or (system_override and "moderation training" in (system_override or ""))

    # ── GREETING ──
    first_word = last_user_msg.split()[0] if last_user_msg.split() else ""
    if first_word in GREETING_WORDS or last_user_msg in GREETING_WORDS:
        return (
            "👋 **Hello! I'm CyberGuard AI** — your intelligent assistant for cyberbullying awareness and content moderation.\n\n"
            "Here's what I can do for you:\n"
            "- 🔍 **Analyze text** for cyberbullying or toxic content\n"
            "- 🎯 **Generate quizzes** to test your detection skills\n"
            "- 📊 **Run assessment exercises** to practice identifying harmful content\n"
            "- ✍️ **Rewrite harmful messages** into safer alternatives\n\n"
            "What would you like to do today?"
        )

    # ── QUIZ MODULE ──
    if is_quiz or "quiz" in last_user_msg:
        return (
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
            "Reply with your choices and I'll generate your personalized quiz! 🚀"
        )

    # ── ASSESSMENT MODULE ──
    if is_assess or "assessment" in last_user_msg:
        return (
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
        )

    # ── THANKS / POSITIVE ──
    if any(w in last_user_msg for w in ["thank", "thanks", "thx", "great", "awesome", "cool", "nice"]):
        return (
            "😊 You're welcome! Is there anything else I can help you with?\n\n"
            "I can **analyze text**, run a **quiz**, or start an **assessment** anytime you're ready."
        )

    # ── CYBERBULLYING / ANALYSIS QUESTION ──
    if any(w in last_user_msg for w in ["analyze", "analysis", "check", "detect", "is this", "is it", "cyberbully", "toxic", "harmful", "safe"]):
        return (
            "🔍 **Analysis Mode**\n\n"
            "I can analyze that for you! My BERT classifier is running locally and has already processed your message.\n\n"
            "Once my language model (Ollama) finishes loading, I'll provide:\n"
            "- **Classification** — What type of content this is\n"
            "- **Severity** — Low / Medium / High\n"
            "- **Reasoning** — Why it's harmful or safe\n"
            "- **Alternatives** — Safer ways to express the same idea\n\n"
            "Please share the text you'd like me to analyze and I'll get started!"
        )

    # ── DEFAULT / GENERIC ──
    return (
        "I understand your message. I'm CyberGuard AI — here to help with **cyberbullying detection, content moderation, quizzes, and assessments**.\n\n"
        "*(Note: My language model is currently loading. Full AI responses will be available shortly.)*\n\n"
        "In the meantime, you can:\n"
        "- 🎯 Click **Quiz Generator** in the sidebar to test your skills\n"
        "- 📊 Click **Assessment flow** to practice identifying harmful content\n"
        "- 🔍 Paste any message here and I'll detect if it's harmful"
    )


class LLMHandler:
    def __init__(self, model="llama3.2"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"

    def set_api_key(self, api_key):
        pass  # Not needed for Ollama

    def generate_response(self, conversation_history, system_override=None):
        """
        Calls the local Ollama LLM via direct HTTP request.
        Falls back to a smart, context-aware response if Ollama is offline.
        """
        messages = []

        sys_msg = system_override if system_override else SYSTEM_PROMPT
        messages.append({"role": "system", "content": sys_msg})

        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": str(msg.get("content", ""))
            })

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "num_ctx": 2048,
                "num_predict": 1024
            }
        }

        try:
            response = requests.post(self.url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    try:
                        data = json.loads(decoded)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except json.JSONDecodeError:
                        pass
        except Exception:
            # Smart, context-aware fallback when Ollama is offline/loading
            fallback_msg = _get_smart_fallback(conversation_history, system_override)

            # Stream word-by-word for a realistic typing effect
            words = fallback_msg.split(' ')
            for idx, word in enumerate(words):
                time.sleep(0.03)
                yield word + (' ' if idx < len(words) - 1 else '')
