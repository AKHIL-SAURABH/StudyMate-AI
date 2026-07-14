# 🎓 StudyMate AI — Comprehensive Test Report

> **Date:** July 14, 2026  
> **Environment:** Windows, Python 3.12.7, `study` venv  
> **Backend:** FastAPI on http://127.0.0.1:8000  
> **Frontend:** Streamlit on http://localhost:8501  
> **LLM:** Groq API (llama-3.3-70b-versatile)

---

## ✅ Test Summary

| Area | Status | Issues Found |
|------|--------|--------------|
| Backend Startup | ✅ Pass | 1 issue (Unicode logging errors) |
| Frontend Startup | ✅ Pass | No issues |
| Auth (Login/Register) | ✅ Pass | No issues |
| Dashboard | ✅ Pass | No issues |
| Sidebar Navigation | ✅ Pass | No issues |
| AI Chat | ✅ Pass | Working well |
| Agent Reasoning Steps | ✅ Pass | Working well |
| MCP Tool Discovery | ✅ Pass | 10 tools discovered |
| MCP Tool Calling | ✅ Pass | Tools execute correctly |
| Quiz Generation | ⚠️ Partial | Quiz renders as text only — no interactive UI |
| Quiz Submission | ❌ Fail | No way to submit answers from UI |
| Quiz History | ⚠️ Partial | Works but always empty (no submissions possible) |
| Subjects Management | ✅ Pass | CRUD works |
| Topics Management | ✅ Pass | CRUD works |
| Progress Dashboard | ✅ Pass | Shows correct data |
| Analytics Page | ✅ Pass | Charts render correctly |
| Settings Page | ⚠️ Partial | Profile fields show blank values |
| Quick Actions | ✅ Pass | All 3 navigate correctly |
| Logout | ✅ Pass | Clears session and returns to login |
| API Auth Guards | ✅ Pass | Returns 401 without auth |
| Error Handling | ✅ Pass | Proper error messages |
| Backend Logging | ❌ Fail | Unicode encoding crashes on Windows |
| Study Preferences Save | ❌ Fail | No save functionality — UI only |

---

## 🐛 Issues Found (Prioritized)

### 🔴 Critical Issues

---

#### 1. Quiz UI Has No Interactive Answer Selection or Submission
**File:** [quiz_ui.py](file:///d:/StudyMate AI/frontend/components/quiz_ui.py#L66-L84)

**Problem:** When a quiz is generated, it's displayed as **plain markdown text** (the AI's response). There are no radio buttons, checkboxes, or any interactive elements to select answers. There is no "Submit" button to score the quiz.

**Impact:** The entire quiz workflow is broken from the user's perspective. Users can read quiz questions but can never:
- Select answers
- Submit answers
- Get scored
- See results in Quiz History
- Have quiz scores reflected in Progress

**Root Cause:** The quiz generator MCP tool returns structured JSON with questions, options, and answers. The quiz router sends this through the AI agent (which reformats it as natural language text). But the UI just renders `quiz.get("response", "")` as markdown (line 74) instead of parsing the structured quiz data and creating interactive form elements.

**Code Path:**
- [quiz router](file:///d:/StudyMate AI/backend/routers/quiz.py#L20-L41): Calls agent to generate quiz → returns `response` text
- [quiz_ui.py](file:///d:/StudyMate AI/frontend/components/quiz_ui.py#L74): Just renders `st.markdown(quiz.get("response", ""))` — no form, no radio buttons

---

#### 2. Backend Logger Unicode Encoding Error on Windows
**File:** [middleware.py](file:///d:/StudyMate AI/backend/middleware.py#L62-L67)

**Problem:** The request logging middleware uses Unicode arrow characters (`→` U+2192 and `←` U+2190) in log messages. On Windows with CP1252 encoding, this causes `UnicodeEncodeError` on **every single HTTP request**.

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 74
```

**Impact:** Continuous error stack traces in the console for every API request. Clutters logs and makes debugging very difficult.

**Fix:** Replace Unicode arrows with ASCII-safe characters:
```python
# Line 62: Change "→" to "->"
logger.info("-> %s %s", method, path)
# Line 67-71: Change "←" to "<-"  
logger.info("<- %s %s [%d] %.1fms", method, path, response.status_code, duration_ms)
```
Also similarly in line 79: `logger.error("✗ %s %s ..." ...)` — replace `✗` with `X` or `FAIL`.

Same issue exists in [main.py](file:///d:/StudyMate AI/backend/main.py#L34-L37) with emoji characters `🚀`, `✅`, `📍`, `👋` in log messages.

---

### 🟡 Medium Issues

---

#### 3. Settings Page Profile Fields Show Blank Values
**File:** [settings_ui.py](file:///d:/StudyMate AI/frontend/components/settings_ui.py#L25-L29)

**Problem:** The profile section shows "Username" and "Email" labels, but the values appear blank in the disabled text inputs.

**Root Cause:** The `st.text_input` uses `value=st.session_state.get("username", "")` and `value=st.session_state.get("email", "")`. These session state keys may not be preserved across Streamlit reruns in certain navigation paths, or the disabled input styling may make the text invisible against the dark theme.

**Impact:** Users cannot see their own profile information on the Settings page.

---

#### 4. Study Preferences Are Not Persisted (Settings Page)
**File:** [settings_ui.py](file:///d:/StudyMate AI/frontend/components/settings_ui.py#L33-L45)

**Problem:** The Settings page has inputs for Study Hours per Day, Learning Style, Preferred Session Length, and Difficulty Preference — but there is **no Save button** and **no API call** to persist these preferences. The `preferences` table exists in the database and gets a default row on registration, but the UI never updates it.

**Impact:** Users configure preferences that are lost on every page reload. The preferences are never used by the AI agent for personalization.

---

#### 5. Settings Page "Show Agent Reasoning" Toggle Not Connected
**File:** [settings_ui.py](file:///d:/StudyMate AI/frontend/components/settings_ui.py#L51)

**Problem:** The toggle uses `key="settings_show_steps"` but the chat page uses `st.session_state.get("show_agent_steps", False)`. These are **different keys** so changing the toggle in Settings does not affect the Chat page.

---

#### 6. No Study Session Logging in the UI
**Files:** [database.py](file:///d:/StudyMate AI/backend/database.py#L53-L66), [analytics_service.py](file:///d:/StudyMate AI/backend/services/analytics_service.py)

**Problem:** The `study_sessions` table exists in the schema but there is **no UI feature to log a study session**. The Analytics page shows "0 sessions", "0.0h study time" and the daily chart says "Study data will appear here as you log sessions!" — but there's no way to log sessions from the UI.

**Impact:** The Analytics page and the Study Streaks section on the Dashboard will always show zeros unless sessions are manually inserted into the database.

---

#### 7. `requirements.txt` Has Duplicate `httpx` Entry
**File:** [requirements.txt](file:///d:/StudyMate AI/requirements.txt#L33-L38)

**Problem:** `httpx==0.28.1` appears twice — once under "Utilities" (line 33) and again under "Testing" (line 38). This is not a breaking issue but is poor practice.

---

### 🟢 Minor / Cosmetic Issues

---

#### 8. Quiz Generator Tool Produces Generic Template Questions
**File:** [quiz_generator.py](file:///d:/StudyMate AI/mcp_server/tools/quiz_generator.py)

**Problem:** The quiz generator MCP tool uses hardcoded template questions (e.g., "What is the fundamental concept of {topic}?") instead of generating topic-specific quiz questions. All quizzes have the same generic structure regardless of topic. A quiz about "Quadratic Equations" vs "Cell Biology" produces nearly identical meta-questions.

**Impact:** Low educational value for users. The quiz doesn't actually test subject knowledge.

---

#### 9. Chat History Not Loaded on Login
**File:** [chat_ui.py](file:///d:/StudyMate AI/frontend/components/chat_ui.py)

**Problem:** When a user logs in, the chat messages list starts empty (`st.session_state.chat_messages = []`). Previous conversations stored in the `memory` table are never loaded into the UI. The API endpoint `GET /api/chat/history/{user_id}` exists but is never called by the frontend.

**Impact:** Users lose their chat history on every login/logout cycle.

---

#### 10. Suggestion Chips Don't Handle Error Responses  
**File:** [chat_ui.py](file:///d:/StudyMate AI/frontend/components/chat_ui.py#L148-L168)

**Problem:** When a suggestion chip is clicked, if the API call fails (`result.get("success")` is False), the error is silently ignored — no error message is appended to the chat. Compare this with the normal chat send flow (lines 126-131) which properly handles errors.

---

#### 11. Subject Difficulty Validator Not Wired as `@field_validator`
**File:** [subject.py](file:///d:/StudyMate AI/backend/models/subject.py#L28-L34)

**Problem:** `validate_difficulty` is defined as a `@classmethod` but is **not decorated with `@field_validator("difficulty_level")`**, so it never runs. Invalid difficulty values (e.g., "extreme") pass validation.

---

#### 12. MCP Client Creates New Connection Per Tool Call
**File:** [client.py](file:///d:/StudyMate AI/mcp_client/client.py#L85-L128)

**Problem:** Every `call_tool()` invocation creates a brand new stdio connection to the MCP server (spawn new process, initialize, call, disconnect). Similarly, `discover_tools()` creates a separate connection. For a single chat message that uses 2 tools, this means:
1. Spawn MCP server → discover tools → close
2. Spawn MCP server → call tool 1 → close
3. Spawn MCP server → call tool 2 → close

**Impact:** Significant latency overhead (each connection takes ~1-2 seconds). A single chat message with tool use takes 10-20+ seconds partly due to this.

---

#### 13. `Groq` Client Used Synchronously Inside `async` Functions
**File:** [llm_client.py](file:///d:/StudyMate AI/agent/llm_client.py#L76-L81)

**Problem:** The `generate()` method is decorated with `@retry_async` and defined as `async def`, but it calls `client.chat.completions.create()` which is a **synchronous blocking call**. This blocks the entire asyncio event loop during LLM inference (which can take 5-15 seconds).

**Impact:** The backend can only handle one chat request at a time. All other requests are blocked while waiting for the LLM.

---

#### 14. No Topic Delete Functionality in UI
**File:** [study_planner_ui.py](file:///d:/StudyMate AI/frontend/components/study_planner_ui.py)

**Problem:** Users can delete subjects (delete button exists) but there is no delete button for individual topics. Once a topic is created, it cannot be removed from the UI.

---

#### 15. `api_client` User ID Not Restored After Page Reload
**File:** [api_client.py](file:///d:/StudyMate AI/frontend/utils/api_client.py#L171-L172)

**Problem:** The `api_client` is a module-level singleton. The `user_id` is set via `set_user()` on login, but on a Streamlit rerun (e.g., page navigation), the singleton may lose its `user_id` since Streamlit reruns the entire script. The `user_id` is in `st.session_state` but the `api_client.user_id` needs to be re-synced.

**Impact:** After certain page navigations, API calls might silently fail with 401 errors because `X-User-ID` header is not sent.

---

## 📊 Feature-by-Feature Test Results

### Authentication
| Test Case | Result | Notes |
|-----------|--------|-------|
| Empty fields login | ✅ | Shows "Please fill in all fields" |
| Wrong credentials login | ✅ | Shows "Invalid username or password" |
| Valid registration | ✅ | Creates account and redirects to dashboard |
| Duplicate registration | ✅ | Shows "User already exists: testuser" |
| Valid login | ✅ | Redirects to dashboard with user data |
| Logout | ✅ | Returns to login page |

### AI Chat & Tool Calling
| Test Case | Result | Notes |
|-----------|--------|-------|
| Simple greeting message | ✅ | Agent responds conversationally |
| Suggestion chip click | ✅ | "Give me motivation" works and calls tools |
| Show Agent Reasoning toggle | ✅ | Displays thought/action/observation/reflection steps |
| Tools used badge | ✅ | Shows which MCP tools were invoked |
| Clear Chat button | ✅ | Clears chat history |

### Subjects & Topics
| Test Case | Result | Notes |
|-----------|--------|-------|
| Add subject | ✅ | Creates and displays immediately |
| Add topic under subject | ✅ | Creates with priority stars |
| Delete subject | ✅ | Removes subject and topics |
| Empty subject name validation | ✅ | Shows warning |

### Quiz
| Test Case | Result | Notes |
|-----------|--------|-------|
| Generate quiz | ✅ | AI generates quiz text |
| Display quiz interactively | ❌ | No radio buttons or answer selection |
| Submit quiz answers | ❌ | No submit functionality |
| Quiz History display | ⚠️ | Works but always empty |
| Generate New Quiz button | ✅ | Resets quiz state |

### Progress & Analytics
| Test Case | Result | Notes |
|-----------|--------|-------|
| Progress metrics | ✅ | Shows correct counts |
| Topic-level progress | ✅ | Shows per-topic confidence |
| Analytics metrics | ✅ | Shows correct (zero) values |
| Plotly charts | ✅ | Render correctly with dark theme |
| Weekly summary | ✅ | Shows correct empty state |

### API Endpoints
| Endpoint | Result | Notes |
|----------|--------|-------|
| `GET /` | ✅ | Health check works |
| `GET /health` | ✅ | Returns model info |
| `GET /docs` | ✅ | Swagger UI accessible |
| `POST /api/auth/register` | ✅ | With validation |
| `POST /api/auth/login` | ✅ | With auth check |
| Unauthenticated access | ✅ | Returns 401 properly |
| Invalid user ID | ✅ | Returns 401 |

---

## 🔧 Recommended Fix Priority

1. **[CRITICAL]** Fix Quiz UI to support interactive answer selection & submission
2. **[CRITICAL]** Fix Unicode logging errors on Windows
3. **[MEDIUM]** Fix Settings profile fields blank values
4. **[MEDIUM]** Add Save button for Study Preferences
5. **[MEDIUM]** Add Study Session logging UI
6. **[MEDIUM]** Wire Settings toggle key to Chat page toggle
7. **[LOW]** Load chat history on login
8. **[LOW]** Handle errors in suggestion chip flow
9. **[LOW]** Fix Subject difficulty validator decorator
10. **[LOW]** Remove duplicate httpx from requirements.txt
11. **[LOW]** Improve quiz generator with topic-specific questions
12. **[LOW]** Add topic delete functionality
13. **[OPTIMIZATION]** Reuse MCP connections instead of spawning per call
14. **[OPTIMIZATION]** Use async Groq client to avoid blocking event loop
15. **[OPTIMIZATION]** Re-sync api_client user_id on every Streamlit rerun
