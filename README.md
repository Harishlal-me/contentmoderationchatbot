# CyberGuard AI — Content Moderation Chatbot

> An intelligent, dual-mode AI assistant for cyberbullying detection and content moderation training.  
> Built with a fine-tuned BERT classifier, a local LLaMA 3.2 LLM (via Ollama), a FastAPI backend, and a React/Vite frontend.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [AI Behavior — Dual Mode System](#ai-behavior--dual-mode-system)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Frontend Components](#frontend-components)
- [Model Details](#model-details)
- [Prompt Engineering](#prompt-engineering)

---

## Project Overview

CyberGuard AI is a full-stack, production-grade AI platform designed for:

- **Real-time cyberbullying and toxicity detection** using a fine-tuned BERT classifier
- **Per-sentence content moderation analysis** powered by LLaMA 3.2 (local LLM via Ollama)
- **Interactive moderation training** through AI-generated Quizzes and Assessments
- **Dual-mode intelligent chatbot** — conversational chat + strict structured analysis

The system is designed to act as a **clinical-grade moderation training tool** and a **research assistant**, not a restrictive public-facing chatbot. It analyzes offensive content without refusal.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  React / Vite Frontend               │
│   ChatView  │  MessageBubble  │  Quiz  │  Assessment │
└────────────────────────┬────────────────────────────┘
                         │  HTTP (streaming)
                         ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend  (api.py)               │
│   POST /api/chat      │      POST /api/command       │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│            ChatController  (chat_controller.py)      │
│                                                     │
│  Intent Detection → BERT Classifier → LLM Handler   │
└──────────┬───────────────────────────┬──────────────┘
           │                           │
           ▼                           ▼
┌──────────────────┐       ┌───────────────────────────┐
│  BERT Classifier │       │   LLaMA 3.2 via Ollama    │
│  (bert_inference │       │   localhost:11434          │
│       .py)       │       │   Streaming HTTP API       │
└──────────────────┘       └───────────────────────────┘
```

---

## Features

### 🤖 Intelligent Dual-Mode Chat
- **Chat Mode**: Natural, friendly conversation — greets, explains, and helps
- **Analysis Mode**: Strict, structured per-sentence toxicity classification
- Automatically switches modes based on detected user intent

### 🔍 Content Moderation Analysis
- Per-sentence classification: `Safe`, `Cyberbullying`, `Hate Speech`, `Harassment`, `Sexual Content`
- Severity rating: `Low`, `Medium`, `High`, `None`
- One-line factual explanation per sentence
- Input cleaning — strips instruction prefixes automatically
- Sentence splitting by punctuation, numbering, and line breaks

### 🎯 Interactive Quiz Module
- AI-generated 5-question MCQ quizzes on cyberbullying detection
- Auto-graded with explanations for each answer
- Strict JSON output from LLM, rendered as interactive UI

### 📊 Scenario Assessment Module
- AI-generated realistic social media scenario paragraphs
- 5 comprehension-based MCQs targeting harm identification and severity
- Full interactive UI with scoring

### 🛡️ BERT Diagnostic Panel
- Real-time threat indicator dot on each AI response
- Confidence score display for flagged messages
- Powered by fine-tuned `bert-base-uncased`

### ⚡ Real-time Streaming
- Word-by-word streamed responses via FastAPI `StreamingResponse`
- Smooth typing effect in the frontend
- Smart offline fallback (context-aware static responses when Ollama is down)

---

## Tech Stack

### Backend
| Component | Technology |
|---|---|
| Web Framework | FastAPI |
| LLM Runtime | Ollama (LLaMA 3.2) |
| BERT Classifier | HuggingFace Transformers (`bert-base-uncased`) |
| Streaming | FastAPI `StreamingResponse` |
| HTTP Client | `requests` (streaming) |
| Legacy UI | Streamlit (`chatbot_app.py`) |

### Frontend
| Component | Technology |
|---|---|
| Framework | React 18 + Vite |
| Styling | TailwindCSS |
| Animations | Framer Motion |
| Markdown | `react-markdown` + `remark-gfm` |
| Icons | Lucide React |
| State | React `useState` / `useRef` hooks |

### AI / ML
| Component | Technology |
|---|---|
| Classifier | Fine-tuned BERT (`bert-base-uncased`) |
| LLM | LLaMA 3.2 (local via Ollama) |
| Training | PyTorch + HuggingFace `Trainer` API |
| Evaluation | scikit-learn metrics (F1, ROC-AUC, PR curve) |

---

## Project Structure

```
promptproject/
│
├── api.py                        # FastAPI server — /api/chat and /api/command endpoints
├── chatbot_app.py                # Legacy Streamlit UI
├── config.py                     # Configuration constants
├── requirements.txt              # Python dependencies
├── readmefinal.md                # This file
│
├── src/
│   ├── chat_controller.py        # Core routing logic — intent detection + BERT + LLM
│   ├── llm_handler.py            # Ollama HTTP streaming + smart offline fallback
│   ├── prompt_templates.py       # All system prompts (SYSTEM, EXPLANATION, SAFE, QUIZ, ASSESS)
│   └── bert_inference.py         # BERT classifier wrapper
│
├── frontend/                     # React/Vite frontend
│   ├── src/
│   │   ├── App.jsx               # Main app shell with sidebar navigation
│   │   ├── App.css               # Global styles
│   │   ├── index.css             # TailwindCSS base
│   │   ├── main.jsx              # React entry point
│   │   └── components/
│   │       ├── ChatView.jsx          # Chat interface, input, streaming
│   │       ├── MessageBubble.jsx     # Message renderer (chat + quiz + assessment)
│   │       ├── QuizComponent.jsx     # Interactive quiz UI
│   │       ├── AssessmentComponent.jsx # Assessment paragraph + MCQ UI
│   │       └── TypingIndicator.jsx   # Loading animation
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── models/                       # Saved BERT model checkpoints
├── data/                         # Training datasets
├── notebooks/                    # Jupyter notebooks for experiments
│
├── bert_classifier.py            # BERT fine-tuning script
├── train_improved.py             # Improved training pipeline
├── evaluate_comprehensive.py     # Full evaluation suite
├── predict_comprehensive.py      # Inference with comprehensive metrics
├── augment_dataset.py            # Dataset augmentation utilities
│
├── confusion_matrix_IMPROVED.png # Model evaluation charts
├── confusion_matrix_ORIGINAL.png
├── roc_curve_IMPROVED.png
├── pr_curve_IMPROVED.png
│
└── MODEL_COMPARISON_REPORT.md    # BERT model comparison (original vs improved)
```

---

## How It Works

### Message Processing Pipeline

```
User Message
     │
     ▼
Intent Detection (_is_analysis_request)
     │
     ├── NOT analysis → LLM (Chat Mode) → Natural response
     │
     └── IS analysis ──→ BERT Classifier
                              │
                              ├── is_threat=True  → SYSTEM_PROMPT + EXPLANATION_PROMPT → LLM
                              │
                              └── is_threat=False → SYSTEM_PROMPT + SAFE_RESPONSE_PROMPT → LLM
                                                              │
                                                         Streaming response
                                                         → FastAPI StreamingResponse
                                                         → React frontend (word-by-word)
```

### Intent Detection Logic

The controller uses **two-layer intent detection**:

1. **Explanation check** (returns `False` for analysis): `"what is"`, `"define"`, `"explain"`, `"how does"` etc.
2. **Analysis triggers** (returns `True`): `"analyze"`, `"classify"`, `"detect"`, `"is this toxic"`, `"check this"`, `"flag this message"`, etc.

This prevents `"what is cyberbullying?"` from being routed into analysis mode.

---

## AI Behavior — Dual Mode System

### Mode 1: Normal Chat (Default)
Activated when no analysis intent is detected.
- Responds naturally and conversationally
- Answers explanatory questions about cyberbullying, moderation concepts, etc.
- Is friendly and helpful in tone

**Examples:**
```
User: "hi"
AI: "Hey! How can I help you today?"

User: "what is cyberbullying?"
AI: [Clear, factual explanation]
```

### Mode 2: Analysis Mode (Strict)
Activated when user explicitly requests text analysis.

**Trigger phrases include:**
- `"analyze this"`, `"classify this"`, `"check this text"`
- `"is this toxic"`, `"is this cyberbullying"`, `"is this offensive"`
- `"flag this message"`, `"rate this message"`, `"detect toxicity"`

**Output format (per sentence):**
```
Sentence 1: "you are stupid"
Classification: Cyberbullying
Severity: Medium
Explanation: Direct personal insult targeting intelligence with intent to demean.

Sentence 2: "have a great day!"
Classification: Safe
Severity: None
Explanation: Positive farewell with no harmful intent.
```

**Rules in analysis mode:**
- Never refuses to analyze, even for offensive content
- Strips instruction prefixes automatically
- Splits input into individual sentences
- Never merges sentences
- No introductory text, warnings, or policy explanations

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.ai) installed and running
- LLaMA 3.2 model pulled: `ollama pull llama3.2`

### 1. Clone the repository
```bash
git clone https://github.com/Harishlal-me/contentmoderationchatbot.git
cd contentmoderationchatbot
```

### 2. Python Backend Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn transformers torch requests streamlit
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Pull the LLM
```bash
ollama pull llama3.2
```

---

## Running the Application

### Start all services (3 terminals):

**Terminal 1 — LLM:**
```bash
ollama run llama3.2
```

**Terminal 2 — FastAPI Backend:**
```bash
uvicorn api:app --reload --port 8000
```

**Terminal 3 — React Frontend:**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

### Optional — Streamlit Legacy UI:
```bash
streamlit run chatbot_app.py
```

---

## API Reference

### `POST /api/chat`
Handles normal user messages. Runs intent detection, BERT, and LLM.

**Request:**
```json
{
  "prompt": "analyze this: you are stupid",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

**Response:** `text/plain` streaming.  
First line: BERT JSON result `{"is_threat": true, "confidence": 0.92, "text": "..."}` followed by `\n|||\n`  
Then: streamed LLM text tokens.

---

### `POST /api/command`
Handles module commands: `QUIZ`, `ASSESS`, `REWRITE`.

**Request:**
```json
{
  "cmd": "QUIZ",
  "metadata": "random_entropy_seed",
  "history": []
}
```

**Response:** `text/plain` streaming — JSON quiz/assessment data from LLM.

---

## Frontend Components

| Component | Responsibility |
|---|---|
| `App.jsx` | Shell layout, sidebar, module state management |
| `ChatView.jsx` | Message list, input form, streaming handler, module switching |
| `MessageBubble.jsx` | Renders user/assistant messages, BERT diagnostic card, quiz/assessment interceptor |
| `QuizComponent.jsx` | Interactive MCQ quiz with auto-grading and explanations |
| `AssessmentComponent.jsx` | Paragraph-based scenario assessment with MCQ scoring |
| `TypingIndicator.jsx` | Animated loading dots while streaming |

---

## Model Details

### BERT Classifier
- **Base model**: `bert-base-uncased`
- **Task**: Binary classification (Safe / Cyberbullying)
- **Training**: Fine-tuned on cyberbullying detection datasets
- **Output**: `is_threat` (bool) + `confidence` (float 0–1)

### LLaMA 3.2 (via Ollama)
- **Runtime**: Ollama local inference server at `localhost:11434`
- **Streaming**: Direct HTTP API with `stream: true`
- **Context window**: 2048 tokens
- **Max output**: 1024 tokens

---

## Prompt Engineering

### Key Prompt Files (`src/prompt_templates.py`)

| Prompt | Purpose |
|---|---|
| `SYSTEM_PROMPT` | Base dual-mode identity and behavior rules |
| `EXPLANATION_PROMPT` | Appended when BERT flags threat — forces structured analysis output |
| `SAFE_RESPONSE_PROMPT` | Appended when BERT says safe — routes to chat or structured safe output |
| `QUIZ_PROMPT` | Forces LLM to output valid JSON quiz structure |
| `ASSESSMENT_PROMPT` | Forces LLM to output valid JSON assessment structure |
| `REWRITE_PROMPT` | Generates 3 safe alternative rewritings of a flagged message |

---

## Contributors

- **Harishlal** — Project Lead, AI/ML Engineering, Full-Stack Development

---

## License

This project is for academic and research purposes only.  
All content moderation analysis is performed for educational training and AI safety research.
