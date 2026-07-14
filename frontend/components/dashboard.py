"""
StudyMate AI — Dashboard Page.

Main dashboard showing key metrics, recent activity,
and quick access to all features.
"""

import streamlit as st

from frontend.utils.api_client import api_client
from frontend.styles.theme import render_metric_card, render_progress_bar


def render_dashboard() -> None:
    """Render the main dashboard page."""
    username = st.session_state.get("username", "Student")

    # Header
    st.markdown(f"""
    <div class="fade-in-up">
        <div class="page-title">Welcome back, {username}! 👋</div>
        <div class="page-subtitle">Here's your study overview</div>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    progress_data = api_client.get_progress()
    analytics_data = api_client.get_analytics()
    weekly_data = api_client.get_weekly_summary()

    # ── Key Metrics Row ────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    if progress_data.get("success"):
        p = progress_data["data"]
        with c1:
            st.markdown(render_metric_card(
                str(p.get("total_subjects", 0)), "Subjects", "📚"
            ), unsafe_allow_html=True)
        with c2:
            st.markdown(render_metric_card(
                str(p.get("total_topics", 0)), "Topics", "📖"
            ), unsafe_allow_html=True)
        with c3:
            st.markdown(render_metric_card(
                f"{p.get('total_study_hours', 0):.1f}h", "Study Time", "⏰"
            ), unsafe_allow_html=True)
        with c4:
            st.markdown(render_metric_card(
                f"{p.get('average_quiz_score', 0):.0f}%", "Avg Quiz Score", "🎯"
            ), unsafe_allow_html=True)
    else:
        for col in [c1, c2, c3, c4]:
            with col:
                st.markdown(render_metric_card("—", "Loading...", "⏳"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two Column Layout ──────────────────────────────────────────
    left_col, right_col = st.columns([3, 2])

    with left_col:
        # Overall Progress
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Overall Progress")

        if progress_data.get("success"):
            p = progress_data["data"]
            total = p.get("total_topics", 0)
            completed = p.get("topics_completed", 0)
            pct = (completed / total * 100) if total > 0 else 0

            st.markdown(render_progress_bar(pct, "Overall Completion"), unsafe_allow_html=True)

            cols = st.columns(3)
            with cols[0]:
                st.metric("✅ Completed", completed)
            with cols[1]:
                st.metric("📝 In Progress", p.get("topics_in_progress", 0))
            with cols[2]:
                st.metric("⬜ Not Started", p.get("topics_not_started", 0))

            # Topic-level progress
            topic_progress = p.get("topic_progress", [])
            if topic_progress:
                st.markdown("#### Topic Breakdown")
                for tp in topic_progress[:8]:
                    confidence = tp.get("confidence_score", 0) * 100
                    st.markdown(
                        render_progress_bar(confidence, f"{tp['topic_name']} ({tp['subject_name']})"),
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Add subjects and topics to see your progress here!")

        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        # Weekly Summary
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📅 This Week")

        if weekly_data.get("success"):
            w = weekly_data["data"]
            hours = w.get("total_minutes", 0) / 60
            st.markdown(f"**Study Time:** {hours:.1f} hours")
            st.markdown(f"**Sessions:** {w.get('sessions_count', 0)}")
            st.markdown(f"**Topics Studied:** {w.get('topics_studied', 0)}")
            st.markdown(f"**Quizzes:** {w.get('quizzes_completed', 0)}")

            if w.get("average_quiz_score", 0) > 0:
                st.markdown(f"**Avg Score:** {w.get('average_quiz_score', 0):.1f}%")

            highlights = w.get("highlights", [])
            if highlights:
                st.markdown("#### Highlights")
                for h in highlights:
                    st.markdown(f"- {h}")
        else:
            st.info("Start studying to see your weekly summary!")

        st.markdown('</div>', unsafe_allow_html=True)

        # Quick Actions
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ⚡ Quick Actions")

        if st.button("💬 Chat with AI Mentor", use_container_width=True, key="dash_chat"):
            st.session_state.current_page = "chat"
            st.rerun()

        if st.button("📝 Take a Quiz", use_container_width=True, key="dash_quiz"):
            st.session_state.current_page = "quiz"
            st.rerun()

        if st.button("📚 Add Subject", use_container_width=True, key="dash_subject"):
            st.session_state.current_page = "study_planner"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Study Streaks ──────────────────────────────────────────────
    if analytics_data.get("success"):
        a = analytics_data["data"]
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        streak_col1, streak_col2, streak_col3 = st.columns(3)
        with streak_col1:
            st.markdown(render_metric_card(
                f"{a.get('current_streak_days', 0)}🔥", "Current Streak", "📆"
            ), unsafe_allow_html=True)
        with streak_col2:
            st.markdown(render_metric_card(
                f"{a.get('longest_streak_days', 0)}⭐", "Longest Streak", "🏆"
            ), unsafe_allow_html=True)
        with streak_col3:
            st.markdown(render_metric_card(
                str(a.get("total_sessions", 0)), "Total Sessions", "📋"
            ), unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
