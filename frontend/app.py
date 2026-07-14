"""
StudyMate AI — Streamlit Application Entry Point.

Main app that handles routing, theme application,
and page rendering based on authentication state.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

from frontend.styles.theme import get_custom_css
from frontend.utils.state import init_session_state, is_authenticated
from frontend.components.auth_ui import render_auth_page
from frontend.components.sidebar import render_sidebar
from frontend.components.dashboard import render_dashboard
from frontend.components.chat_ui import render_chat_page
from frontend.components.study_planner_ui import render_study_planner
from frontend.components.progress_ui import render_progress_page
from frontend.components.quiz_ui import render_quiz_page
from frontend.components.analytics_ui import render_analytics_page
from frontend.components.settings_ui import render_settings_page


# ── Page Configuration ─────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyMate AI — AI Study Mentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "StudyMate AI — An AI-powered Study Mentor built with Agentic AI and MCP.",
    },
)

# ── Apply Custom Theme ─────────────────────────────────────────────────
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Initialize Session State ──────────────────────────────────────────
init_session_state()


# ── Main App Logic ─────────────────────────────────────────────────────
def main() -> None:
    """Main application entry point."""
    if not is_authenticated():
        render_auth_page()
        return

    # Ensure api_client user_id is synced from session state on every rerun
    from frontend.utils.api_client import api_client
    api_client.user_id = st.session_state.get("user_id")

    # Render sidebar navigation
    render_sidebar()

    # Route to the current page
    page = st.session_state.get("current_page", "dashboard")

    page_map = {
        "dashboard": render_dashboard,
        "chat": render_chat_page,
        "study_planner": render_study_planner,
        "progress": render_progress_page,
        "quiz": render_quiz_page,
        "analytics": render_analytics_page,
        "settings": render_settings_page,
    }

    renderer = page_map.get(page, render_dashboard)
    renderer()


if __name__ == "__main__":
    main()
