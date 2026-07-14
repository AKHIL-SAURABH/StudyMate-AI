# StudyMate AI — Installation Guide

## Prerequisites

- **Python 3.11+** (download from [python.org](https://python.org))
- **Groq API Key** (get one free at [console.groq.com/keys](https://console.groq.com/keys))

## Step-by-Step Setup

### 1. Create Virtual Environment

```bash
cd "StudyMate AI"
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and set your Groq API key:
```
GROQ_API_KEY=gsk_your_key_here
```

### 4. Start the Backend

```bash
python -m backend.main
```

Verify it's running: open `http://127.0.0.1:8000/docs` in your browser.

### 5. Start the Frontend

Open a **new terminal**, activate the venv, and run:

```bash
streamlit run frontend/app.py
```

The app opens at `http://localhost:8501`.

### 6. First Use

1. Click **Register** to create an account
2. Add subjects and topics in the **Subjects** page
3. Chat with the AI mentor in the **AI Chat** page
4. Take quizzes in the **Quiz** section
5. Track progress in the **Progress Dashboard**

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `ModuleNotFoundError` | Ensure venv is activated and dependencies installed |
| `GROQ_API_KEY not set` | Check your `.env` file has the key |
| `Cannot connect to API` | Start the backend before the frontend |
| `MCP server failed` | Check that `mcp` and `fastmcp` packages are installed |
