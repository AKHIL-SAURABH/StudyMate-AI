# StudyMate AI — API Reference

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
All authenticated endpoints require the `X-User-ID` header with a valid user ID.

---

## Auth Endpoints

### POST `/api/auth/register`
Register a new user.
```json
{
  "username": "student1",
  "email": "student@example.com",
  "password": "securepass123"
}
```

### POST `/api/auth/login`
Authenticate with credentials.
```json
{
  "username": "student1",
  "password": "securepass123"
}
```

### GET `/api/auth/me`
Get current user profile. **Requires auth header.**

---

## Chat Endpoints

### POST `/api/chat/message`
Send a message to the AI agent. **Requires auth header.**
```json
{
  "message": "Create a study plan for my math exam",
  "conversation_id": "optional-existing-id"
}
```
Response includes `agent_steps` and `tools_used` for transparency.

### GET `/api/chat/history/{user_id}`
Get conversation history.

---

## Subject Endpoints

### POST `/api/subjects/`
Create subject. **Requires auth header.**

### GET `/api/subjects/`
List all subjects with topics. **Requires auth header.**

### POST `/api/subjects/{id}/topics`
Add topic to subject.

### DELETE `/api/subjects/{id}`
Delete subject (cascades to topics).

---

## Progress Endpoints

### GET `/api/progress/`
Get progress overview. **Requires auth header.**

### POST `/api/progress/update`
Update topic confidence score.

---

## Quiz Endpoints

### POST `/api/quiz/generate`
Generate AI quiz. **Requires auth header.**

### POST `/api/quiz/submit`
Submit quiz answers for scoring.

### GET `/api/quiz/history`
Get quiz score history.

---

## Analytics Endpoints

### GET `/api/analytics/`
Get comprehensive study analytics. **Requires auth header.**

### GET `/api/analytics/weekly`
Get weekly study summary.

---

## Health Check

### GET `/health`
```json
{
  "status": "healthy",
  "service": "StudyMate AI",
  "llm_model": "llama-3.3-70b-versatile",
  "database": "connected"
}
```
