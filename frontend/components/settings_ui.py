"""
StudyMate AI — Settings Page UI.

User preferences and application settings.
"""

import streamlit as st

from frontend.utils.state import clear_user


def render_settings_page() -> None:
    """Render the settings page."""
    from frontend.utils.api_client import api_client

    # Fallback to load profile if session state is missing username/email
    if not st.session_state.get("username") or not st.session_state.get("email"):
        profile_res = api_client.get_me()
        if profile_res.get("success"):
            data = profile_res.get("data", {})
            st.session_state.username = data.get("username")
            st.session_state.email = data.get("email")

    # Load preferences from backend if not cached
    if "user_preferences" not in st.session_state:
        pref_res = api_client.get_preferences()
        if pref_res.get("success"):
            st.session_state.user_preferences = pref_res.get("data", {})
        else:
            st.session_state.user_preferences = {}

    prefs = st.session_state.user_preferences
    default_hours = prefs.get("study_hours_per_day", 4.0)
    default_length = prefs.get("preferred_session_length", 45)
    
    styles = ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"]
    style_val = prefs.get("learning_style", "visual").capitalize()
    default_style_idx = styles.index(style_val) if style_val in styles else 0

    difficulties = ["Easy", "Medium", "Hard"]
    diff_val = prefs.get("difficulty_preference", "medium").capitalize()
    default_diff_idx = difficulties.index(diff_val) if diff_val in difficulties else 1

    st.markdown("""
    <div class="fade-in-up">
        <div class="page-title">⚙️ Settings</div>
        <div class="page-subtitle">Manage your profile and study preferences</div>
    </div>
    """, unsafe_allow_html=True)

    # Profile section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 👤 Profile")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Username", value=st.session_state.get("username", ""), disabled=True)
    with col2:
        st.text_input("Email", value=st.session_state.get("email", ""), disabled=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Study Preferences
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📚 Study Preferences")

    col1, col2 = st.columns(2)
    with col1:
        hours = st.number_input("Study Hours per Day", min_value=0.5, max_value=16.0, value=float(default_hours), step=0.5)
        style = st.selectbox("Learning Style", styles, index=default_style_idx)
    with col2:
        length = st.number_input("Preferred Session Length (min)", min_value=15, max_value=120, value=int(default_length), step=15)
        difficulty = st.selectbox("Difficulty Preference", difficulties, index=default_diff_idx)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Save Preferences", use_container_width=True):
        with st.spinner("Saving preferences..."):
            save_res = api_client.save_preferences(
                hours=hours,
                length=length,
                difficulty=difficulty,
                style=style,
            )
        if save_res.get("success"):
            st.success("Preferences saved successfully!")
            st.session_state.user_preferences = {
                "study_hours_per_day": hours,
                "preferred_session_length": length,
                "difficulty_preference": difficulty,
                "learning_style": style,
            }
            st.rerun()
        else:
            st.error("Failed to save preferences.")

    st.markdown('</div>', unsafe_allow_html=True)

    # AI Settings
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Settings")

    st.toggle("Show Agent Reasoning Steps in Chat", key="show_agent_steps")

    st.markdown("""
    **LLM Model:** llama-3.3-70b-versatile (Groq API)  
    **Fallback Model:** qwen3-32b  
    **Architecture:** ReAct Loop with MCP Tools
    """)

    st.markdown('</div>', unsafe_allow_html=True)

    # About
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ℹ️ About StudyMate AI")

    st.markdown("""
    **StudyMate AI** is an AI-powered study mentor built with:
    
    - 🧠 **Agentic AI** with ReAct Reasoning Loop
    - 🔧 **MCP** (Model Context Protocol) for tool orchestration
    - ⚡ **Groq API** for fast LLM inference
    - 🏗️ **FastAPI** backend with clean architecture
    - 💾 **SQLite** database with 10 tables
    - 🎨 **Streamlit** frontend with dark theme
    
    The AI agent dynamically discovers and uses 10 educational tools:
    Study Planner, Quiz Generator, Resource Finder, Revision Planner,
    Weak Topic Analyzer, Progress Tracker, Motivation Generator,
    Study Statistics, Subject Analyzer, and Time Estimator.
    
    **Version:** 1.0.0
    """)

    st.markdown('</div>', unsafe_allow_html=True)

    # Danger zone
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ⚠️ Account")

    if st.button("🚪 Logout", use_container_width=True):
        clear_user()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
