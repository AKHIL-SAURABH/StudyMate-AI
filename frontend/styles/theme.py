"""
StudyMate AI — Streamlit Theme & CSS.

Defines the dark theme, custom CSS, and color palette
for a modern, premium dashboard experience.
"""


# ── Color Palette ──────────────────────────────────────────────────────
COLORS = {
    "bg_primary": "#0f0f1a",
    "bg_secondary": "#1a1a2e",
    "bg_card": "#16213e",
    "bg_hover": "#1f3460",
    "accent_primary": "#7c3aed",      # Violet
    "accent_secondary": "#06b6d4",    # Cyan
    "accent_success": "#10b981",      # Emerald
    "accent_warning": "#f59e0b",      # Amber
    "accent_danger": "#ef4444",       # Red
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "border": "#334155",
    "gradient_start": "#7c3aed",
    "gradient_end": "#06b6d4",
}


def get_custom_css() -> str:
    """
    Generate the complete custom CSS for the Streamlit app.

    Returns:
        CSS string with dark theme, glassmorphism, animations, and component styles.
    """
    return f"""
    <style>
        /* ── Global Reset & Dark Theme ─────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        .stApp {{
            background: linear-gradient(135deg, {COLORS['bg_primary']} 0%, {COLORS['bg_secondary']} 50%, #0a0a23 100%);
            color: {COLORS['text_primary']};
            font-family: 'Inter', sans-serif;
        }}

        /* ── Sidebar ───────────────────────────────────────────────── */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_primary']} 100%);
            border-right: 1px solid {COLORS['border']};
        }}

        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {{
            color: {COLORS['text_primary']};
        }}

        /* ── Cards / Glass Effect ──────────────────────────────────── */
        .glass-card {{
            background: rgba(22, 33, 62, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(124, 58, 237, 0.15);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
        }}

        .glass-card:hover {{
            border-color: rgba(124, 58, 237, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(124, 58, 237, 0.15);
        }}

        /* ── Metric Cards ──────────────────────────────────────────── */
        .metric-card {{
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(124, 58, 237, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(124, 58, 237, 0.2);
        }}

        .metric-value {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, {COLORS['accent_primary']}, {COLORS['accent_secondary']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 8px 0;
        }}

        .metric-label {{
            font-size: 0.85rem;
            color: {COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* ── Buttons ───────────────────────────────────────────────── */
        .stButton > button {{
            background: linear-gradient(135deg, {COLORS['accent_primary']} 0%, #6d28d9 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 24px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
        }}

        /* ── Inputs ────────────────────────────────────────────────── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background: rgba(22, 33, 62, 0.5) !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 10px !important;
            color: {COLORS['text_primary']} !important;
            font-family: 'Inter', sans-serif !important;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {COLORS['accent_primary']} !important;
            box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
        }}

        /* ── Select Box ────────────────────────────────────────────── */
        .stSelectbox > div > div {{
            background: rgba(22, 33, 62, 0.5) !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 10px !important;
        }}

        /* ── Chat Messages ─────────────────────────────────────────── */
        .chat-user {{
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(124, 58, 237, 0.05) 100%);
            border: 1px solid rgba(124, 58, 237, 0.2);
            border-radius: 16px 16px 4px 16px;
            padding: 16px 20px;
            margin: 8px 0;
            animation: fadeInRight 0.3s ease;
        }}

        .chat-assistant {{
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(6, 182, 212, 0.03) 100%);
            border: 1px solid rgba(6, 182, 212, 0.15);
            border-radius: 16px 16px 16px 4px;
            padding: 16px 20px;
            margin: 8px 0;
            animation: fadeInLeft 0.3s ease;
        }}

        /* ── Progress Bar ──────────────────────────────────────────── */
        .progress-bar-container {{
            background: rgba(51, 65, 85, 0.3);
            border-radius: 10px;
            overflow: hidden;
            height: 10px;
            margin: 8px 0;
        }}

        .progress-bar-fill {{
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, {COLORS['accent_primary']}, {COLORS['accent_secondary']});
            transition: width 1s ease;
        }}

        /* ── Animations ────────────────────────────────────────────── */
        @keyframes fadeInRight {{
            from {{ opacity: 0; transform: translateX(20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}

        @keyframes fadeInLeft {{
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.6; }}
        }}

        .fade-in-up {{
            animation: fadeInUp 0.5s ease;
        }}

        /* ── Headers ───────────────────────────────────────────────── */
        .page-title {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, {COLORS['accent_primary']}, {COLORS['accent_secondary']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}

        .page-subtitle {{
            color: {COLORS['text_secondary']};
            font-size: 1rem;
            margin-bottom: 24px;
        }}

        /* ── Status Badges ─────────────────────────────────────────── */
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .badge-success {{
            background: rgba(16, 185, 129, 0.15);
            color: {COLORS['accent_success']};
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .badge-warning {{
            background: rgba(245, 158, 11, 0.15);
            color: {COLORS['accent_warning']};
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        .badge-danger {{
            background: rgba(239, 68, 68, 0.15);
            color: {COLORS['accent_danger']};
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        /* ── Tabs ──────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            background: rgba(22, 33, 62, 0.3);
            border-radius: 12px;
            padding: 4px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            color: {COLORS['text_secondary']};
            font-weight: 500;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {COLORS['accent_primary']}, #6d28d9);
            color: white;
        }}

        /* ── Expander ──────────────────────────────────────────────── */
        .streamlit-expanderHeader {{
            background: rgba(22, 33, 62, 0.4);
            border-radius: 10px;
            border: 1px solid {COLORS['border']};
        }}

        /* ── Scrollbar ─────────────────────────────────────────────── */
        ::-webkit-scrollbar {{
            width: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: {COLORS['bg_primary']};
        }}

        ::-webkit-scrollbar-thumb {{
            background: {COLORS['border']};
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS['accent_primary']};
        }}
    </style>
    """


def render_metric_card(value: str, label: str, icon: str = "") -> str:
    """
    Render a styled metric card.

    Args:
        value: The metric value to display.
        label: Label for the metric.
        icon: Optional emoji icon.

    Returns:
        HTML string for the metric card.
    """
    return f"""
    <div class="metric-card">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def render_progress_bar(percentage: float, label: str = "") -> str:
    """
    Render a styled progress bar.

    Args:
        percentage: Progress percentage (0-100).
        label: Optional label text.

    Returns:
        HTML string for the progress bar.
    """
    pct = max(0, min(100, percentage))
    return f"""
    <div>
        {f'<div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 4px;">{label} — {pct:.1f}%</div>' if label else ''}
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {pct}%;"></div>
        </div>
    </div>
    """
