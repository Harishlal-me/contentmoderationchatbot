<div align="center">

# 🛡️ CyberGuard AI: Advanced Content Moderation Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.1+-blue.svg)](https://react.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama_Llama_3.2-black.svg)](https://ollama.ai/)

**A dual-engine, real-time content moderation platform and educational AI assistant.**

</div>

---

## 🌟 Overview

The **CyberGuard AI Platform** is an advanced content moderation chatbot and educational assistant designed to detect, analyze, and educate users on cyberbullying and harmful online behavior. 

Unlike traditional rule-based filters, CyberGuard utilizes a **Hybrid AI Pipeline**—fusing a blazing-fast local **BERT deep learning model** for immediate threat classification with an **Ollama-powered Local LLM (Llama 3.2)** for deep semantic analysis, reasoning, and context-awareness. It now includes a **Behavior Performance Tracker** to monitor user trends in real-time.

---

## 🏗️ System Architecture

The chatbot is built with modularity and local execution in mind, ensuring data privacy and zero API costs.

### 1. 🧠 Core AI Engines (The Brains)
- **BERT Classifier (`src/bert_classifier.py` & `src/bert_inference.py`)**: A fine-tuned `bert-base-uncased` PyTorch model. It processes every incoming message instantly, assigning a confidence score and determining if the text is a potential threat.
- **LLM Handler (`src/llm_handler.py`)**: Connects to a local Ollama instance running Llama 3.2 (`http://localhost:11434/api/chat`). Handles streaming responses, sentence-level semantic breakdowns, and generation of quizzes/assessments. Features a smart fallback mechanism if the local LLM is offline.
- **Decision Engine (`src/decision_engine.py`)**: The ultimate arbitrator. It fuses the BERT confidence score, LLM sentence-level severity analysis, and hardcoded Regex rules (detecting threats, slurs, spam) to calculate a final **0-100 Risk Score** and enforce a moderation policy (`Block`, `Warn`, or `Allow`).

### 2. 🚦 The Controller (`src/chat_controller.py`)
Acts as the central router for the application:
- **Intent Detection**: Analyzes user input to route the request dynamically. Explanatory questions (e.g., *"What is cyberbullying?"*) stay in standard **Chat Mode**, while moderation triggers (e.g., *"Analyze this text"*) activate the deep **Analysis Mode**.
- **Command Management**: Processes discrete system commands like `QUIZ` (generates MCQs), `ASSESS` (generates situational paragraphs), and `REWRITE` (generates safe alternatives to toxic text).
- **Behavioral Pipeline**: Tracks historical toxicity across the session to detect escalation patterns and provide "Repeated harmful behavior" signals to the LLM.

### 4. 📊 Analysis Dashboard (The Insights)
A unified, real-time dashboard built with **Chart.js** that provides:
- **Risk Trend Graph**: Visualizes the volatility of user behavior over a timeline.
- **Performance Insight**: Intelligent interpretation of behavior (e.g., "Behavior is worsening").
- **Dynamic Suggestion Engine**: Context-aware tips to improve communication.
- **Conversation Breakdown**: Detailed history with trend indicators and status icons.

### 3. 🖥️ The Client Interfaces
CyberGuard exposes its capabilities via two primary interfaces:
- **FastAPI / React Backend (`api.py` + `frontend/`)**: A modular API exposing endpoints like `/api/chat` and `/api/command` via SSE (Server-Sent Events) for real-time text streaming. A separate Vite/React frontend consumes these endpoints.
- **Streamlit Premium Dashboard (`chatbot_app.py`)**: A monolithic, SaaS-styled UI featuring rich data visualizations, interactive chat bubbles, expandable technical moderation pipelines, and risk-score progress bars.

---

## 🔍 The Moderation Pipeline

When a user submits text for analysis, the chatbot executes the following end-to-end pipeline:

1. **User Input parsing**: The request is intercepted and intent is analyzed.
2. **Text Preprocessing**: Normalization, URL handling, and mention extraction.
3. **BERT Classification**: Extracts immediate threat probability (e.g., 96.8% Confidence).
4. **Context Injection**: Selects appropriate system prompts based on the BERT verdict (`SAFE_RESPONSE_PROMPT` vs. `EXPLANATION_PROMPT`).
5. **Behavioral Context Builder**: Injects the last 5 messages and historical risk scores into the LLM prompt to detect escalation or patterns.
6. **LLM Sentence Analysis**: The local Llama model breaks down the text sentence-by-sentence, inferring semantics, sarcasm, and nuanced intent.
7. **Rule-Based Mapping**: Cross-references outputs with hardcoded RegEx limits mapped to severity weights (*High=1.0, Medium=0.55, Low=0.25*).
8. **Decision Engine Synthesis**: Calculates the unified Risk Score.
9. **Action Enforcement**: Returns structured JSON determining if the message is `Safe`, requires `Review`, or is strictly `Unsafe`.
10. **Analysis Dashboard Sync**: The **Behavior Performance Tracker** updates live with risk graphs, trend insights, and timestamped message breakdowns.
11. **UI Rendering**: Streams the explanation using a strict Markdown engine followed by the live-updating analysis indicators.

---

## 🎒 Educational Modules

Beyond moderation, the chatbot acts as a trainer for human moderators:

- **📝 Quiz Generation**: Using the `QUIZ_PROMPT`, the system generates dynamic, mixed-difficulty multiple-choice questions assessing the user's ability to identify toxic context.
- **📊 Assessment Scenarios**: The `ASSESS_PROMPT` engineers realistic paragraphs containing mixed payloads (normal text + subtle abuse). Users evaluate which sentences belong to which severity tiers.
- **♻️ Content Rewriting**: Given an offensive piece of text, the `REWRITE` command instructs the LLM to provide de-escalated, safe alternatives while preserving the underlying message intent.

---

## 🛠️ Usage & Commands

### Running the Services

To run the full stack locally, open separate terminal windows for the following:

**1. Start the Local LLM Daemon:**
```bash
ollama serve
# (Ensure llama3.2 is pulled: ollama run llama3.2)
```

**2. Start the Backend API (FastAPI):**
```bash
uvicorn api:app --reload --port 8000
```

**3. Start the React Frontend:**
```bash
cd frontend
npm install
npm run dev
# Accessible at http://localhost:5173
```

**4. (Alternative) Start the Streamlit Application:**
```bash
streamlit run chatbot_app.py
# Accessible at http://localhost:8501
```

### Chatbot Keywords / Triggers
- **Analysis Execution:** Type words like `analyze`, `classify`, `moderate this` directly to the bot.
- **Educational Help:** Ask `What is cyberbullying?` to trigger safe chat definitions without launching the heavy moderation pipeline.

---

## 🧠 Decision Engine Metrics

The **Risk Score** formula balances hard deep-learning mathematics with NLP semantics:
* **High Risk (70-100%)**: Contains severe insults, hate speech, or direct threats. Triggers `🚫 Block` action.
* **Medium Risk (40-69%)**: Contains ambiguous slang, indirect insults, or aggressive spam. Triggers `⚠️ Warn` action.
* **Low Risk (0-39%)**: Casual language, verified positive context ("You're killing it out there!"), or general chat. Triggers `✅ Allow` action.
