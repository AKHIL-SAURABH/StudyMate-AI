"""
StudyMate AI — Study Planner UI.

Subject and topic management interface with CRUD operations.
"""

import streamlit as st

from frontend.utils.api_client import api_client


def render_study_planner() -> None:
    """Render the study planner / subjects page."""
    st.markdown("""
    <div class="fade-in-up">
        <div class="page-title">📚 Subjects & Topics</div>
        <div class="page-subtitle">Manage your subjects and topics to help the AI personalize your study plan</div>
    </div>
    """, unsafe_allow_html=True)

    # Add Subject Form
    with st.expander("➕ Add New Subject", expanded=False):
        with st.form("add_subject_form"):
            s_name = st.text_input("Subject Name", placeholder="e.g., Mathematics, Physics, Python")
            s_desc = st.text_area("Description (optional)", placeholder="Brief description of the subject", height=80)
            s_diff = st.selectbox("Difficulty Level", ["easy", "medium", "hard"], index=1)

            if st.form_submit_button("📚 Add Subject", use_container_width=True):
                if s_name.strip():
                    result = api_client.create_subject(s_name.strip(), s_desc.strip(), s_diff)
                    if result.get("success"):
                        st.success(f"Subject '{s_name}' added!")
                        st.rerun()
                    else:
                        st.error(result.get("error", {}).get("message", "Failed to add subject"))
                else:
                    st.warning("Please enter a subject name")

    # Load subjects
    subjects_result = api_client.get_subjects()

    if not subjects_result.get("success"):
        st.error("Failed to load subjects. Is the backend running?")
        return

    subjects = subjects_result.get("data", [])

    if not subjects:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px;">
            <div style="font-size: 3rem;">📚</div>
            <div style="font-size: 1.2rem; color: #f1f5f9; margin: 12px 0;">No subjects yet</div>
            <div style="color: #94a3b8;">Add your first subject to get started with personalized study plans!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Display subjects
    for subj in subjects:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)

            # Subject header
            header_col, action_col = st.columns([4, 1])
            with header_col:
                difficulty_badges = {
                    "easy": "🟢 Easy",
                    "medium": "🟡 Medium",
                    "hard": "🔴 Hard",
                }
                badge = difficulty_badges.get(subj.get("difficulty_level", "medium"), "🟡 Medium")
                st.markdown(f"### {subj['name']}  `{badge}`")
                if subj.get("description"):
                    st.markdown(f"*{subj['description']}*")

            with action_col:
                if st.button("🗑️", key=f"del_subj_{subj['id']}", help="Delete subject"):
                    api_client.delete_subject(subj["id"])
                    st.rerun()

            # Topics
            topics = subj.get("topics", [])

            if topics:
                st.markdown("**Topics:**")
                for topic in topics:
                    status_icons = {
                        "not_started": "⬜",
                        "in_progress": "🟡",
                        "completed": "✅",
                    }
                    icon = status_icons.get(topic.get("status", "not_started"), "⬜")
                    priority = "⭐" * topic.get("priority", 3)

                    t_col1, t_col2 = st.columns([12, 1])
                    with t_col1:
                        st.markdown(f"- {icon} **{topic['name']}** — Priority: {priority}")
                    with t_col2:
                        if st.button("🗑️", key=f"del_topic_{topic['id']}", help=f"Delete topic '{topic['name']}'"):
                            api_client.delete_topic(topic["id"])
                            st.rerun()
            else:
                st.info("No topics yet. Add topics below.")

            # Add Topic Form
            with st.expander(f"➕ Add Topic to {subj['name']}", expanded=False):
                with st.form(f"add_topic_{subj['id']}"):
                    t_name = st.text_input("Topic Name", key=f"tn_{subj['id']}")
                    t_desc = st.text_input("Description (optional)", key=f"td_{subj['id']}")
                    t_priority = st.slider("Priority", 1, 5, 3, key=f"tp_{subj['id']}")

                    if st.form_submit_button("Add Topic"):
                        if t_name.strip():
                            result = api_client.create_topic(subj["id"], t_name.strip(), t_desc.strip(), t_priority)
                            if result.get("success"):
                                st.success(f"Topic '{t_name}' added!")
                                st.rerun()
                            else:
                                st.error("Failed to add topic")
                        else:
                            st.warning("Enter a topic name")

            # Log Study Session Form
            if topics:
                with st.expander(f"⏰ Log Study Session for {subj['name']}", expanded=False):
                    with st.form(f"log_session_{subj['id']}"):
                        session_topic = st.selectbox(
                            "Select Topic",
                            options=topics,
                            format_func=lambda x: x["name"],
                            key=f"session_topic_sel_{subj['id']}",
                        )
                        session_duration = st.number_input(
                            "Duration (minutes)",
                            min_value=1,
                            max_value=720,
                            value=30,
                            step=5,
                            key=f"session_dur_{subj['id']}",
                        )
                        session_notes = st.text_input(
                            "Study Notes (optional)",
                            placeholder="What did you study?",
                            key=f"session_notes_{subj['id']}",
                        )
                        
                        if st.form_submit_button("⏰ Log Session"):
                            res = api_client.log_study_session(
                                subject_id=subj["id"],
                                topic_id=session_topic["id"],
                                duration=session_duration,
                                notes=session_notes,
                            )
                            if res.get("success"):
                                st.success("Session logged successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to log study session.")

            st.markdown('</div>', unsafe_allow_html=True)
