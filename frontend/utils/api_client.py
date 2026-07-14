"""
StudyMate AI — API Client.

HTTP client for the Streamlit frontend to communicate
with the FastAPI backend.
"""

import requests
from typing import Any, Optional

API_BASE_URL = "http://127.0.0.1:8000"


class APIClient:
    """HTTP client for FastAPI backend communication."""

    def __init__(self, base_url: str = API_BASE_URL) -> None:
        self.base_url = base_url
        self.user_id: Optional[str] = None

    def _headers(self) -> dict[str, str]:
        """Build request headers with user ID."""
        headers = {"Content-Type": "application/json"}
        if self.user_id:
            headers["X-User-ID"] = self.user_id
        return headers

    def _request(
        self, method: str, endpoint: str, data: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET/POST/DELETE).
            endpoint: API endpoint path.
            data: Optional JSON body data.

        Returns:
            Response JSON dict.
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                resp = requests.get(url, headers=self._headers(), timeout=60)
            elif method == "POST":
                resp = requests.post(url, json=data, headers=self._headers(), timeout=60)
            elif method == "DELETE":
                resp = requests.delete(url, headers=self._headers(), timeout=60)
            else:
                return {"success": False, "error": {"message": f"Unknown method: {method}"}}

            result = resp.json()

            if resp.status_code >= 400:
                error = result.get("error", result.get("detail", {}))
                if isinstance(error, dict):
                    return {"success": False, "error": error}
                return {"success": False, "error": {"message": str(error)}}

            return result

        except requests.ConnectionError:
            return {
                "success": False,
                "error": {"message": "Cannot connect to the API server. Is the backend running?"},
            }
        except requests.Timeout:
            return {
                "success": False,
                "error": {"message": "Request timed out. The server may be processing a complex query."},
            }
        except Exception as exc:
            return {"success": False, "error": {"message": str(exc)}}

    # ── Auth Endpoints ─────────────────────────────────────────────

    def register(self, username: str, email: str, password: str) -> dict:
        """Register a new user."""
        return self._request("POST", "/api/auth/register", {
            "username": username, "email": email, "password": password,
        })

    def login(self, username: str, password: str) -> dict:
        """Login with credentials."""
        return self._request("POST", "/api/auth/login", {
            "username": username, "password": password,
        })

    def get_me(self) -> dict:
        """Get current user profile."""
        return self._request("GET", "/api/auth/me")

    # ── Chat Endpoints ─────────────────────────────────────────────

    def send_message(self, message: str, conversation_id: Optional[str] = None) -> dict:
        """Send a message to the AI agent."""
        data = {"message": message}
        if conversation_id:
            data["conversation_id"] = conversation_id
        return self._request("POST", "/api/chat/message", data)

    def get_chat_history(self) -> dict:
        """Get chat history for current user."""
        return self._request("GET", f"/api/chat/history/{self.user_id}")

    # ── Subject Endpoints ──────────────────────────────────────────

    def create_subject(self, name: str, description: str = "", difficulty: str = "medium") -> dict:
        """Create a new subject."""
        return self._request("POST", "/api/subjects/", {
            "name": name, "description": description, "difficulty_level": difficulty,
        })

    def get_subjects(self) -> dict:
        """Get all subjects for the current user."""
        return self._request("GET", "/api/subjects/")

    def create_topic(self, subject_id: str, name: str, description: str = "", priority: int = 3) -> dict:
        """Create a topic under a subject."""
        return self._request("POST", f"/api/subjects/{subject_id}/topics", {
            "name": name, "description": description, "priority": priority,
        })

    def delete_subject(self, subject_id: str) -> dict:
        """Delete a subject."""
        return self._request("DELETE", f"/api/subjects/{subject_id}")

    def delete_topic(self, topic_id: str) -> dict:
        """Delete a topic."""
        return self._request("DELETE", f"/api/subjects/topics/{topic_id}")

    def log_study_session(self, subject_id: Optional[str], topic_id: Optional[str], duration: int, notes: str = "") -> dict:
        """Log a study session."""
        return self._request("POST", "/api/subjects/sessions", {
            "subject_id": subject_id,
            "topic_id": topic_id,
            "duration_minutes": duration,
            "notes": notes,
        })

    # ── Progress Endpoints ─────────────────────────────────────────

    def get_progress(self) -> dict:
        """Get progress overview."""
        return self._request("GET", "/api/progress/")

    def update_progress(self, topic_id: str, confidence: float) -> dict:
        """Update topic progress."""
        return self._request("POST", "/api/progress/update", {
            "topic_id": topic_id, "confidence_score": confidence,
        })

    # ── Quiz Endpoints ─────────────────────────────────────────────

    def generate_quiz(self, topic: str, difficulty: str = "medium", num_questions: int = 5) -> dict:
        """Generate a quiz."""
        return self._request("POST", "/api/quiz/generate", {
            "topic": topic, "difficulty": difficulty, "num_questions": num_questions,
        })

    def submit_quiz(self, answers: dict, quiz_data: dict, topic_id: Optional[str] = None) -> dict:
        """Submit quiz answers."""
        return self._request("POST", "/api/quiz/submit", {
            "answers": answers, "quiz_data": quiz_data, "topic_id": topic_id,
        })

    def get_quiz_history(self) -> dict:
        """Get quiz score history."""
        return self._request("GET", "/api/quiz/history")

    # ── Analytics Endpoints ────────────────────────────────────────

    def get_analytics(self) -> dict:
        """Get study analytics."""
        return self._request("GET", "/api/analytics/")

    def get_weekly_summary(self) -> dict:
        """Get weekly study summary."""
        return self._request("GET", "/api/analytics/weekly")

    def get_preferences(self) -> dict:
        """Get study preferences."""
        return self._request("GET", "/api/auth/preferences")

    def save_preferences(self, hours: float, length: int, difficulty: str, style: str) -> dict:
        """Save study preferences."""
        return self._request("POST", "/api/auth/preferences", {
            "study_hours_per_day": hours,
            "preferred_session_length": length,
            "difficulty_preference": difficulty,
            "learning_style": style,
        })


# Singleton client
api_client = APIClient()
