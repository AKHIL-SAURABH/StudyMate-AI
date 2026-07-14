"""
StudyMate AI — Sidebar Navigation.

Renders the navigation sidebar with page links and user info.
"""

import streamlit as st

from frontend.utils.state import navigate_to, clear_user


def render_sidebar() -> None:
    """Render the navigation sidebar."""
    with st.sidebar:
        # Logo / Brand
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 2.5rem;">🎓</div>
            <div style="font-size: 1.4rem; font-weight: 700;
                        background: linear-gradient(135deg, #7c3aed, #06b6d4);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;">
                StudyMate AI
            </div>
            <div style="color: #94a3b8; font-size: 0.8rem;">AI-Powered Study Mentor</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User Info
        username = st.session_state.get("username", "Student")
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 16px;">
            <div style="font-size: 1.8rem;">👤</div>
            <div style="color: #f1f5f9; font-weight: 600;">{username}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        pages = [
            ("🏠", "Dashboard", "dashboard"),
            ("💬", "AI Chat", "chat"),
            ("📚", "Subjects", "study_planner"),
            ("📊", "Progress", "progress"),
            ("📝", "Quiz", "quiz"),
            ("📈", "Analytics", "analytics"),
            ("⚙️", "Settings", "settings"),
        ]

        current_page = st.session_state.get("current_page", "dashboard")

        for icon, label, page_id in pages:
            is_active = current_page == page_id
            button_style = "primary" if is_active else "secondary"

            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type=button_style,
            ):
                navigate_to(page_id)
                st.rerun()

        st.markdown("---")

        # Logout
        if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
            clear_user()
            st.rerun()

        # Footer
        st.markdown("""
        <div style="text-align: center; padding: 16px 0; color: #64748b; font-size: 0.75rem;">
            Powered by Groq AI<br>
            StudyMate AI v1.0
        </div>
        """, unsafe_allow_html=True)
