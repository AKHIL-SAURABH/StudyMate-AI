"""
StudyMate AI — Analytics Page UI.

Comprehensive study analytics with charts and insights.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from frontend.utils.api_client import api_client
from frontend.styles.theme import render_metric_card, COLORS


def render_analytics_page() -> None:
    """Render the analytics page."""
    st.markdown("""
    <div class="fade-in-up">
        <div class="page-title">📈 Study Analytics</div>
        <div class="page-subtitle">Deep insights into your study patterns and performance</div>
    </div>
    """, unsafe_allow_html=True)

    result = api_client.get_analytics()

    if not result.get("success"):
        st.error("Failed to load analytics. Is the backend running?")
        return

    data = result["data"]

    # Summary row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        hours = data.get("total_study_minutes", 0) / 60
        st.markdown(render_metric_card(f"{hours:.1f}h", "Total Study Time", "⏰"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_metric_card(
            str(data.get("total_sessions", 0)), "Total Sessions", "📋"
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(render_metric_card(
            f"{data.get('average_session_length', 0):.0f}m", "Avg Session", "⌛"
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(render_metric_card(
            f"{data.get('current_streak_days', 0)}🔥", "Streak", "📆"
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    left, right = st.columns(2)

    with left:
        # Study time chart
        daily_data = data.get("daily_data", [])

        if daily_data:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Daily Study Time")

            dates = [d["date"] for d in daily_data]
            minutes = [d["minutes_studied"] for d in daily_data]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dates, y=minutes,
                marker=dict(
                    color=minutes,
                    colorscale=[[0, COLORS["accent_primary"]], [1, COLORS["accent_secondary"]]],
                ),
                hovertemplate="Date: %{x}<br>Minutes: %{y}<extra></extra>",
            ))
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=COLORS["text_secondary"]),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.3)", title="Minutes"),
                margin=dict(l=40, r=20, t=20, b=40),
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="glass-card" style="text-align: center; padding: 40px;">', unsafe_allow_html=True)
            st.markdown("### 📊 Daily Study Time")
            st.info("Study data will appear here as you log sessions!")
            st.markdown('</div>', unsafe_allow_html=True)

    with right:
        # Subject breakdown
        subject_breakdown = data.get("subject_breakdown", [])

        if subject_breakdown:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📚 Subject Breakdown")

            labels = [s["subject_name"] for s in subject_breakdown]
            values = [s["total_minutes"] for s in subject_breakdown]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker=dict(colors=[
                    COLORS["accent_primary"],
                    COLORS["accent_secondary"],
                    COLORS["accent_success"],
                    COLORS["accent_warning"],
                    "#8b5cf6",
                    "#ec4899",
                ]),
                textinfo="label+percent",
                textfont=dict(color="white"),
            )])
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=COLORS["text_secondary"]),
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="glass-card" style="text-align: center; padding: 40px;">', unsafe_allow_html=True)
            st.markdown("### 📚 Subject Breakdown")
            st.info("Add subjects and log study sessions to see the breakdown!")
            st.markdown('</div>', unsafe_allow_html=True)

    # Insights
    insights = data.get("insights", [])
    if insights:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Insights")
        for insight in insights:
            st.markdown(f"- {insight}")
        st.markdown('</div>', unsafe_allow_html=True)
