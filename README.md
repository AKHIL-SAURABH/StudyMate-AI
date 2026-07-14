# 🎓 StudyMate AI

> An AI-powered Study Mentor built with Agentic AI, MCP Architecture, and Groq LLM

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Overview

StudyMate AI is a **production-grade Agentic AI** application that serves as a personalized study mentor for students preparing for exams. It demonstrates key AI concepts:

- 🧠 **Agentic AI** — Autonomous reasoning and decision-making
- 🔄 **ReAct Loop** — Thought → Action → Observation → Repeat → Final
- 🔧 **MCP (Model Context Protocol)** — Dynamic tool discovery and invocation
- 🪞 **Self-Reflection** — The AI reviews its own answers before delivery
- 💾 **Persistent Memory** — Remembers conversations across sessions

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI    │ ◄── Dark theme, dashboard, chat, analytics
└────────┬────────┘
         │ HTTP REST
┌────────▼────────┐
│  FastAPI Backend │ ◄── Routers, services, middleware, validation
└────────┬────────┘
         │
┌────────▼────────┐
│ Agent Controller │ ◄── Pipeline orchestration
└────────┬────────┘
         │
┌────────▼────────┐
│  ReAct Loop      │ ◄── Thought → Action → Observation → Repeat
│  + Reflection    │
└───┬─────────┬───┘
    │         │
┌───▼───┐ ┌──▼──────┐
│ Groq  │ │MCP Client│ ◄── Dynamic tool discovery
│ LLM   │ └──┬──────┘
└───────┘    │ stdio
         ┌───▼──────┐
         │MCP Server │ ◄── 10 educational tools
         └───┬──────┘
             │
         ┌───▼──────┐
         │  SQLite   │ ◄── 10 tables, persistent storage
         └──────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python, FastAPI, Pydantic |
| **Frontend** | Streamlit |
| **LLM** | Groq API (llama-3.3-70b-versatile) |
| **Protocol** | MCP (Model Context Protocol) |
| **Database** | SQLite (aiosqlite) |
| **Auth** | bcrypt |

## 🔧 MCP Tools (10)

| Tool | Description |
|------|-------------|
| `study_planner` | Day-by-day study schedules |
| `quiz_generator` | MCQ quiz generation |
| `resource_finder` | Study resource recommendations |
| `revision_planner` | Spaced-repetition scheduling |
| `weak_topic_analyzer` | Identifies weak areas from scores |
| `progress_tracker` | Comprehensive progress view |
| `motivation_generator` | Motivational content + streaks |
| `study_statistics` | Study time analytics |
| `subject_analyzer` | Subject readiness assessment |
| `time_estimator` | Time needed per topic |

## 📁 Project Structure

```
StudyMate AI/
├── backend/          # FastAPI backend
│   ├── main.py       # App entry point
│   ├── config.py     # Configuration
│   ├── database.py   # SQLite + schema
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic
│   └── routers/      # API endpoints
├── agent/            # AI Agent core
│   ├── controller.py # Pipeline orchestrator
│   ├── react_loop.py # ReAct engine
│   ├── reflection.py # Self-reflection
│   ├── llm_client.py # Groq API wrapper
│   ├── memory_manager.py
│   └── prompts/      # 6 engineered prompts
├── mcp_server/       # MCP Server
│   ├── server.py     # FastMCP setup
│   └── tools/        # 10 educational tools
├── mcp_client/       # MCP Client
│   └── client.py     # Tool discovery + invocation
├── frontend/         # Streamlit UI
│   ├── app.py        # Main app
│   ├── components/   # 8 UI pages
│   ├── styles/       # Dark theme + CSS
│   └── utils/        # API client + state
├── utils/            # Shared utilities
├── tests/            # Unit + API tests
└── docs/             # Documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com/keys)

### Installation

```bash
# 1. Clone and enter the project
cd "StudyMate AI"

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the Application

You need **two terminals**:

**Terminal 1 — FastAPI Backend:**
```bash
cd "StudyMate AI"
python -m backend.main
```
The API will be available at `http://127.0.0.1:8000`
API docs at `http://127.0.0.1:8000/docs`

**Terminal 2 — Streamlit Frontend:**
```bash
cd "StudyMate AI"
streamlit run frontend/app.py
```
The UI will open at `http://localhost:8501`

### Running Tests

```bash
python -m pytest tests/ -v
```

## 🗃️ Database Schema

10 tables: `users`, `subjects`, `topics`, `study_sessions`, `progress`, `quiz_scores`, `revision_history`, `preferences`, `memory`, `agent_logs`

## 🧠 Agent ReAct Workflow

```
User Message
    ↓
Load Memory + Context
    ↓
Discover MCP Tools (dynamic)
    ↓
┌─── ReAct Loop (max 5 iterations) ───┐
│  LLM → Thought + Action Decision    │
│  If tool_call → MCP → Observation   │
│  If final_answer → Break            │
└──────────────────────────────────────┘
    ↓
Self-Reflection (quality review)
    ↓
Save Memory + Agent Logs
    ↓
Return Response
```

## 📝 Prompt Engineering

6 specialized prompts:
1. **System Prompt** — Agent identity and behavioral rules
2. **Tool Calling Prompt** — Structured JSON output for ReAct
3. **Reflection Prompt** — Quality review checklist
4. **JSON Repair Prompt** — Malformed output recovery
5. **Memory Prompt** — Conversation summarization
6. **Planner Prompt** — Study plan generation

## 🔮 Future Improvements

- [ ] JWT authentication with refresh tokens
- [ ] WebSocket real-time chat
- [ ] PDF/document upload and analysis
- [ ] Spaced repetition algorithm (SM-2)
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Collaborative study groups
- [ ] Export study plans to PDF/Calendar
- [ ] Mobile-responsive PWA

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.
