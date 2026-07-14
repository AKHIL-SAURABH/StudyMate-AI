# StudyMate AI — Architecture Documentation

## System Architecture

StudyMate AI follows a **Clean Architecture** pattern with clear separation between layers:

### Layer Diagram

```
┌──────────────────────────────────────────────┐
│              PRESENTATION LAYER               │
│  Streamlit UI (frontend/)                     │
│  - 8 pages: Auth, Dashboard, Chat, Quiz...    │
│  - Custom dark theme with glassmorphism       │
│  - Session state management                   │
└────────────────────┬─────────────────────────┘
                     │ HTTP REST (requests)
┌────────────────────▼─────────────────────────┐
│              API LAYER                        │
│  FastAPI (backend/)                           │
│  - 6 routers (auth, chat, subjects, etc.)     │
│  - Pydantic validation                        │
│  - CORS, logging, error handling middleware    │
│  - Dependency injection                       │
└────────────────────┬─────────────────────────┘
                     │
┌────────────────────▼─────────────────────────┐
│              AGENT LAYER                      │
│  Agent Controller → ReAct Loop → Reflection   │
│  - Groq LLM Client (primary + fallback)       │
│  - MCP Client (dynamic tool discovery)         │
│  - Memory Manager (short + long term)          │
│  - 6 engineered prompts                        │
└───────┬───────────────────────────┬──────────┘
        │                           │ stdio
┌───────▼───────┐          ┌───────▼──────────┐
│   Groq API    │          │   MCP Server     │
│   (Cloud LLM) │          │   10 tools       │
└───────────────┘          └───────┬──────────┘
                                   │
                           ┌───────▼──────────┐
                           │    SQLite DB      │
                           │    10 tables      │
                           └──────────────────┘
```

### Data Flow

1. **User sends message** via Streamlit → HTTP POST to FastAPI
2. **FastAPI validates** request with Pydantic, routes to Agent Controller
3. **Agent Controller** loads memory, discovers MCP tools
4. **ReAct Loop** asks Groq LLM to reason and decide actions
5. **LLM chooses tools** → MCP Client invokes them on MCP Server
6. **Tool results** feed back into the loop as observations
7. **Reflection Engine** reviews the draft answer via another LLM call
8. **Memory Manager** persists the conversation and agent logs
9. **Response** flows back through FastAPI to Streamlit

### Key Design Decisions

- **Groq API only** — No local model required, fast inference
- **stdio transport for MCP** — MCP server runs as subprocess, clean lifecycle
- **Async everything** — aiosqlite, async FastAPI, async agent pipeline
- **Singleton services** — Efficient resource usage for single-process deployment
- **SQLite WAL mode** — Better concurrent read performance
