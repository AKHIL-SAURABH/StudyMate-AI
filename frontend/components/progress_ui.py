"""
StudyMate AI — Progress Dashboard UI.

Visual progress tracking across subjects and topics.
"""

import streamlit as st

from frontend.utils.api_client import api_client
from frontend.styles.theme import render_metric_card, render_progress_bar


def render_progress_page() -> None:
    """Render the progress dashboard page."""
    st.markdown("""
    <div class="fade-in-up">
        <div class="page-title">📊 Progress Dashboard</div>
        <div class="page-subtitle">Track your study progress across all subjects and topics</div>
    </div>
    """, unsafe_allow_html=True)

    result = api_client.get_progress()

    if not result.get("success"):
        st.error("Failed to load progress data. Is the backend running?")
        return

    data = result["data"]

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_metric_card(
            f"{data.get('average_confidence', 0):.0%}", "Avg Confidence", "🎯"
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(render_metric_card(
            f"{data.get('topics_completed', 0)}/{data.get('total_topics', 0)}",
            "Topics Done", "✅"
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(render_metric_card(
            f"{data.get('total_study_hours', 0):.1f}h", "Study Hours", "⏰"
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(render_metric_card(
            f"{data.get('average_quiz_score', 0):.0f}%", "Quiz Average", "📝"
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Overall progress bar
    total = data.get("total_topics", 0)
    completed = data.get("topics_completed", 0)
    pct = (completed / total * 100) if total > 0 else 0

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Overall Completion")
    st.markdown(render_progress_bar(pct, f"{completed} of {total} topics completed"), unsafe_allow_html=True)

    # Status breakdown
    cols = st.columns(3)
    with cols[0]:
        st.success(f"✅ Completed: {data.get('topics_completed', 0)}")
    with cols[1]:
        st.warning(f"📝 In Progress: {data.get('topics_in_progress', 0)}")
    with cols[2]:
        st.info(f"⬜ Not Started: {data.get('topics_not_started', 0)}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Per-topic progress
    topic_progress = data.get("topic_progress", [])

    if topic_progress:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📚 Topic-Level Progress")

        for tp in topic_progress:
            confidence = tp.get("confidence_score", 0) * 100
            name = tp.get("topic_name", "Unknown")
            subject = tp.get("subject_name", "")
            status = tp.get("status", "not_started")
            rev_count = tp.get("revision_count", 0)

            status_badge = {"not_started": "⬜", "in_progress": "🟡", "completed": "✅"}.get(status, "⬜")

            st.markdown(f"**{status_badge} {name}** ({subject}) — Revisions: {rev_count}")
            st.markdown(render_progress_bar(confidence, f"Confidence: {confidence:.0f}%"), unsafe_allow_html=True)

            if tp.get("next_review"):
                st.caption(f"📅 Next review: {tp['next_review'][:10]}")

            st.markdown("---")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📚 Add subjects and take quizzes to see topic-level progress!")
