"""
StudyMate AI — Authentication UI.

Login and registration page with animated design.
"""

import streamlit as st

from frontend.utils.api_client import api_client
from frontend.utils.state import set_user


def render_auth_page() -> None:
    """Render the login/register page."""
    # Centered header
    st.markdown("""
    <div style="text-align: center; padding: 40px 0 20px;">
        <div style="font-size: 4rem; margin-bottom: 8px;">🎓</div>
        <div class="page-title" style="font-size: 2.5rem;">StudyMate AI</div>
        <div class="page-subtitle">Your AI-Powered Study Mentor</div>
    </div>
    """, unsafe_allow_html=True)

    # Auth tabs
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)

            with st.form("login_form"):
                st.markdown("### Welcome Back!")
                username = st.text_input("Username", placeholder="Enter your username", key="login_user")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

                submitted = st.form_submit_button("🚀 Login", use_container_width=True)

                if submitted:
                    if not username or not password:
                        st.error("Please fill in all fields")
                    else:
                        with st.spinner("Authenticating..."):
                            result = api_client.login(username, password)

                        if result.get("success"):
                            set_user(result["data"])
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            error = result.get("error", {})
                            st.error(error.get("message", "Login failed"))

            st.markdown('</div>', unsafe_allow_html=True)

        with tab_register:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)

            with st.form("register_form"):
                st.markdown("### Create Account")
                new_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
                new_email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
                new_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pass")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_confirm")

                submitted = st.form_submit_button("✨ Create Account", use_container_width=True)

                if submitted:
                    if not all([new_username, new_email, new_password, confirm_password]):
                        st.error("Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            result = api_client.register(new_username, new_email, new_password)

                        if result.get("success"):
                            set_user(result["data"])
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            error = result.get("error", {})
                            st.error(error.get("message", "Registration failed"))

            st.markdown('</div>', unsafe_allow_html=True)

    # Features showcase
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 24px;">What StudyMate AI Can Do For You</div>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)

    features = [
        ("🤖", "AI Study Mentor", "Personalized guidance powered by advanced AI"),
        ("📋", "Study Plans", "Day-by-day schedules tailored to your goals"),
        ("📝", "Smart Quizzes", "AI-generated quizzes to test your knowledge"),
        ("📊", "Progress Tracking", "Visual analytics to track your journey"),
    ]

    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; min-height: 160px;">
                <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
                <div style="color: #f1f5f9; font-weight: 600; margin-bottom: 4px;">{title}</div>
                <div style="color: #94a3b8; font-size: 0.85rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
