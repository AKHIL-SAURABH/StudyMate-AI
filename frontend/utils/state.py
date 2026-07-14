"""
StudyMate AI — Session State Management.

Manages Streamlit session state for authentication,
navigation, and UI state persistence.
"""

import streamlit as st
from typing import Any, Optional


def init_session_state() -> None:
    """Initialize all session state variables with defaults."""
    defaults = {
        # Auth
        "authenticated": False,
        "user_id": None,
        "username": None,
        "email": None,
        # Navigation
        "current_page": "dashboard",
        # Chat
        "chat_messages": [],
        "conversation_id": None,
        "show_agent_steps": False,
        # Quiz
        "current_quiz": None,
        "quiz_answers": {},
        "quiz_submitted": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_user(user_data: dict) -> None:
    """Set authenticated user in session state."""
    st.session_state.authenticated = True
    st.session_state.user_id = user_data.get("id")
    st.session_state.username = user_data.get("username")
    st.session_state.email = user_data.get("email")

    # Set user_id on the API client
    from frontend.utils.api_client import api_client
    api_client.user_id = user_data.get("id")


def clear_user() -> None:
    """Clear user session (logout)."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.chat_messages = []
    st.session_state.conversation_id = None

    from frontend.utils.api_client import api_client
    api_client.user_id = None


def navigate_to(page: str) -> None:
    """Navigate to a page."""
    st.session_state.current_page = page


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)


def get_user_id() -> Optional[str]:
    """Get current user ID."""
    return st.session_state.get("user_id")
