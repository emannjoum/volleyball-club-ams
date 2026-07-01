"""Shared visual theme for the JVC Streamlit app."""

# ── Palette ────────────────────────────────────────────────────────────────

DARK = {
    "page_bg": "#090B10",
    "page_gradient": "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99,116,142,0.12) 0%, transparent 60%)",
    "surface": "rgba(255, 255, 255, 0.035)",
    "surface_hover": "rgba(255, 255, 255, 0.055)",
    "surface_solid": "#12151C",
    "card_bg": "rgba(255, 255, 255, 0.04)",
    "panel_bg": "rgba(255, 255, 255, 0.03)",
    "text_primary": "#ECEEF2",
    "text_secondary": "#8B95A8",
    "text_muted": "#5C6578",
    "border": "rgba(255, 255, 255, 0.07)",
    "border_strong": "rgba(255, 255, 255, 0.11)",
    "accent": "#7C8EF5",
    "accent_soft": "rgba(124, 142, 245, 0.14)",
    "accent_warm": "#D4A574",
    "success": "#5CB88A",
    "danger": "#E06B6B",
    "warning": "#D4A574",
    "grid_empty": "rgba(255, 255, 255, 0.06)",
    "scroll_thumb": "rgba(255, 255, 255, 0.12)",
    "scroll_track": "transparent",
    "sidebar_bg": "linear-gradient(180deg, #0C0E14 0%, #090B10 100%)",
    "input_bg": "rgba(255, 255, 255, 0.04)",
    "shadow_sm": "0 1px 2px rgba(0,0,0,0.25), 0 4px 16px rgba(0,0,0,0.12)",
    "shadow_md": "0 4px 24px rgba(0,0,0,0.22), 0 1px 3px rgba(0,0,0,0.15)",
    "shadow_lg": "0 12px 40px rgba(0,0,0,0.35)",
    "radar_label": "#C8CED8",
}

LIGHT = {
    "page_bg": "#F5F6F8",
    "page_gradient": "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(124,142,245,0.08) 0%, transparent 60%)",
    "surface": "rgba(255, 255, 255, 0.85)",
    "surface_hover": "#FFFFFF",
    "surface_solid": "#FFFFFF",
    "card_bg": "rgba(255, 255, 255, 0.92)",
    "panel_bg": "rgba(255, 255, 255, 0.75)",
    "text_primary": "#151820",
    "text_secondary": "#5C6578",
    "text_muted": "#8B95A8",
    "border": "rgba(15, 23, 42, 0.08)",
    "border_strong": "rgba(15, 23, 42, 0.12)",
    "accent": "#5B6FD6",
    "accent_soft": "rgba(91, 111, 214, 0.1)",
    "accent_warm": "#B8894E",
    "success": "#3D9B72",
    "danger": "#D45454",
    "warning": "#B8894E",
    "grid_empty": "rgba(15, 23, 42, 0.08)",
    "scroll_thumb": "rgba(15, 23, 42, 0.15)",
    "scroll_track": "transparent",
    "sidebar_bg": "linear-gradient(180deg, #FFFFFF 0%, #F5F6F8 100%)",
    "input_bg": "rgba(255, 255, 255, 0.95)",
    "shadow_sm": "0 1px 2px rgba(15,23,42,0.04), 0 4px 16px rgba(15,23,42,0.06)",
    "shadow_md": "0 4px 24px rgba(15,23,42,0.08), 0 1px 3px rgba(15,23,42,0.04)",
    "shadow_lg": "0 12px 40px rgba(15,23,42,0.1)",
    "radar_label": "#374151",
}


def tokens(light_mode: bool) -> dict:
    return LIGHT if light_mode else DARK


def inject_login_css() -> None:
  import streamlit as st

  st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
        background: #090B10 !important;
        color: #ECEEF2 !important;
    }

    #MainMenu, footer, header { visibility: hidden; height: 0; }

    .block-container {
        padding-top: 5vh !important;
        max-width: 440px !important;
    }

    /* Ambient backdrop */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 70% 45% at 50% -10%, rgba(124,142,245,0.14) 0%, transparent 55%),
            radial-gradient(ellipse 40% 30% at 90% 80%, rgba(212,165,116,0.06) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="column"]:nth-of-type(2) {
        position: relative;
        background: rgba(255, 255, 255, 0.035);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2.25rem 2rem 1.75rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05);
    }

    /* Tabs */
    div[data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.07);
        padding: 4px;
        gap: 4px;
        margin-bottom: 1.25rem;
    }
    div[data-baseweb="tab-highlight"] { display: none !important; }
    button[data-baseweb="tab"] {
        flex: 1;
        justify-content: center;
        background: transparent !important;
        border-radius: 9px !important;
        margin: 0 !important;
        padding: 0.65rem 1rem !important;
        border: none !important;
        color: #8B95A8 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s ease !important;
    }
    button[aria-selected="true"][data-baseweb="tab"] {
        background: rgba(124, 142, 245, 0.2) !important;
        color: #ECEEF2 !important;
        box-shadow: inset 0 0 0 1px rgba(124,142,245,0.35);
    }

    /* Labels */
    .stSelectbox label p, .stTextInput label p {
        color: #8B95A8 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
        text-transform: none !important;
    }

    /* Inputs */
    div[data-baseweb="select"] > div,
    input[type="password"], input[type="text"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 11px !important;
        color: #ECEEF2 !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-baseweb="select"] > div:focus-within,
    input:focus {
        border-color: rgba(124,142,245,0.45) !important;
        box-shadow: 0 0 0 3px rgba(124,142,245,0.12) !important;
    }

    .stButton > button {
        background: #7C8EF5 !important;
        color: white !important;
        width: 100% !important;
        border-radius: 11px !important;
        padding: 0.72rem 1rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        border: none !important;
        margin-top: 0.35rem !important;
        box-shadow: 0 4px 16px rgba(124,142,245,0.28) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        background: #6B7DE8 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 22px rgba(124,142,245,0.35) !important;
    }

    /* Hide the decorative disabled PIN spacer */
    [data-testid="column"]:nth-of-type(2) [data-testid="column"]:last-child .stTextInput {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
  )


def inject_global_css(light_mode: bool) -> dict:
    import streamlit as st

    t = tokens(light_mode)
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Source Sans 3', sans-serif;
            background-color: {t["page_bg"]} !important;
            color: {t["text_primary"]} !important;
        }}

        .stApp {{
            background: {t["page_bg"]} !important;
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: {t["page_gradient"]};
            pointer-events: none;
            z-index: 0;
        }}

        #MainMenu, footer {{ visibility: hidden; }}
        .block-container {{
            padding: 1.25rem 2rem 2.5rem !important;
            max-width: 1140px !important;
        }}

        ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        ::-webkit-scrollbar-track {{ background: {t["scroll_track"]}; }}
        ::-webkit-scrollbar-thumb {{
            background: {t["scroll_thumb"]};
            border-radius: 99px;
        }}

        /* ── Typography ── */
        .page-hero {{
            margin-bottom: 1.75rem;
            padding-bottom: 1.1rem;
            border-bottom: 1px solid {t["border"]};
        }}
        .hero-eyebrow {{
            font-family: 'Outfit', sans-serif;
            font-size: 0.72rem;
            font-weight: 500;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: {t["text_muted"]};
            display: block;
            margin-bottom: 0.35rem;
        }}
        .hero-title {{
            font-family: 'Outfit', sans-serif;
            font-size: clamp(1.65rem, 3.5vw, 2.35rem);
            font-weight: 600;
            color: {t["text_primary"]};
            line-height: 1.15;
            letter-spacing: -0.025em;
            margin: 0;
        }}
        .hero-accent {{ color: {t["accent"]}; font-weight: 600; }}

        .section-header {{ margin: 0 0 0.9rem 0; }}
        .section-eyebrow {{
            font-size: 0.7rem;
            font-weight: 500;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: {t["text_muted"]};
            display: block;
            margin-bottom: 0.15rem;
        }}
        .section-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.05rem;
            font-weight: 600;
            color: {t["text_primary"]};
            margin: 0;
            letter-spacing: -0.01em;
        }}

        /* ── Native Streamlit bordered containers ── */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: {t["panel_bg"]} !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {t["border"]} !important;
            border-radius: 18px !important;
            padding: 0.35rem 0.5rem !important;
            box-shadow: {t["shadow_sm"]};
        }}
        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            padding: 0.65rem 0.75rem !important;
        }}

        /* ── Panels (HTML-only sections) ── */
        .content-panel {{
            background: {t["panel_bg"]};
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {t["border"]};
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 0.5rem;
            box-shadow: {t["shadow_sm"]};
        }}

        /* ── Stat cards ── */
        .stat-card {{
            position: relative;
            background: {t["card_bg"]};
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid {t["border"]};
            border-radius: 16px;
            padding: 1.15rem 1.25rem;
            margin-bottom: 0.5rem;
            box-shadow: {t["shadow_sm"]};
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            overflow: hidden;
        }}
        .stat-card::before {{
            content: "";
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 3px;
            background: var(--card-accent, {t["accent"]});
            border-radius: 16px 0 0 16px;
            opacity: 0.85;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: {t["shadow_md"]};
            border-color: {t["border_strong"]};
        }}
        .card-label {{
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.01em !important;
            text-transform: none !important;
            color: {t["text_secondary"]} !important;
            margin: 0 0 0.4rem 0 !important;
        }}
        .card-value {{
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.75rem !important;
            font-weight: 600 !important;
            line-height: 1.15 !important;
            margin: 0 !important;
            letter-spacing: -0.02em !important;
        }}
        .card-sub {{
            font-size: 0.78rem;
            color: {t["text_muted"]};
            margin-top: 0.25rem;
            display: block;
        }}

        .helper-text {{
            font-size: 0.88rem;
            color: {t["text_secondary"]};
            line-height: 1.5;
            margin: 0.2rem 0 0.75rem 0;
        }}

        /* ── Status badges ── */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            font-size: 0.84rem;
            font-weight: 500;
            padding: 0.4rem 0.85rem;
            border-radius: 99px;
            margin-bottom: 0.75rem;
        }}
        .status-in {{
            background: rgba(92, 184, 138, 0.12);
            color: {t["success"]};
            border: 1px solid rgba(92, 184, 138, 0.22);
        }}
        .status-out {{
            background: rgba(224, 107, 107, 0.1);
            color: {t["danger"]};
            border: 1px solid rgba(224, 107, 107, 0.2);
        }}
        .status-dot {{
            width: 7px; height: 7px;
            border-radius: 50%;
            background: currentColor;
            flex-shrink: 0;
        }}

        /* ── Streak list ── */
        .streak-list {{ display: flex; flex-direction: column; gap: 6px; }}
        .streak-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 12px;
            padding: 0.55rem 0.8rem;
            transition: background 0.15s ease;
        }}
        .streak-row:hover {{ background: {t["surface_hover"]}; }}
        .streak-rank {{
            font-size: 0.9rem;
            width: 22px;
            text-align: center;
            flex-shrink: 0;
            color: {t["text_muted"]};
        }}
        .streak-info {{ flex: 1; min-width: 0; }}
        .streak-name {{
            font-size: 0.84rem;
            font-weight: 500;
            color: {t["text_primary"]};
            display: block;
            margin-bottom: 5px;
        }}
        .streak-bar-wrap {{
            height: 5px;
            background: {t["grid_empty"]};
            border-radius: 99px;
            overflow: hidden;
        }}
        .streak-bar {{
            height: 100%;
            border-radius: 99px;
            background: {t["accent"]};
            opacity: 0.75;
            transition: width 0.5s ease;
        }}
        .streak-count {{
            font-family: 'Outfit', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            color: {t["accent"]};
            width: 26px;
            text-align: right;
            flex-shrink: 0;
        }}

        /* ── Skill bars ── */
        .skill-breakdown {{ display: flex; flex-direction: column; gap: 9px; margin-top: 0.6rem; }}
        .skill-row {{ display: flex; align-items: center; gap: 10px; }}
        .skill-label {{
            font-size: 0.8rem;
            font-weight: 500;
            color: {t["text_secondary"]};
            width: 58px;
            flex-shrink: 0;
        }}
        .skill-bar-wrap {{
            flex: 1;
            height: 6px;
            background: {t["grid_empty"]};
            border-radius: 99px;
            overflow: hidden;
        }}
        .skill-bar-fill {{
            height: 100%;
            border-radius: 99px;
            background: {t["accent"]};
            opacity: 0.8;
            transition: width 0.5s ease;
        }}
        .skill-num {{
            font-size: 0.78rem;
            font-weight: 500;
            color: {t["text_muted"]};
            width: 30px;
            text-align: right;
        }}

        /* ── Activity grid ── */
        .activity-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            padding: 0.5rem 0;
        }}
        .activity-square {{
            width: 16px; height: 16px;
            border-radius: 4px;
            cursor: default;
            transition: transform 0.12s ease, opacity 0.12s ease;
            opacity: 0.9;
        }}
        .activity-square:hover {{ transform: scale(1.35); opacity: 1; }}

        /* ── Pills & chips ── */
        .player-pill-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            padding: 0.35rem 0;
        }}
        .player-pill {{
            background: {t["accent_soft"]};
            color: {t["accent"]};
            border: 1px solid rgba(124,142,245,0.2);
            border-radius: 99px;
            padding: 0.22rem 0.65rem;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        .session-chip {{
            display: inline-block;
            background: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 11px;
            padding: 0.42rem 0.85rem;
            font-size: 0.86rem;
            font-weight: 500;
            color: {t["text_primary"]};
        }}
        .cancelled-chip {{
            background: rgba(224, 107, 107, 0.08);
            border-color: rgba(224, 107, 107, 0.18);
            color: {t["danger"]};
            text-decoration: line-through;
            opacity: 0.85;
        }}

        .info-bar {{
            background: {t["accent_soft"]};
            border: 1px solid rgba(124,142,245,0.15);
            border-radius: 12px;
            padding: 0.65rem 1rem;
            font-size: 0.86rem;
            color: {t["text_secondary"]};
            line-height: 1.55;
            margin-bottom: 0.85rem;
        }}
        .info-bar b {{ color: {t["text_primary"]}; font-weight: 600; }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background: {t["sidebar_bg"]} !important;
            border-right: 1px solid {t["border"]} !important;
        }}
        section[data-testid="stSidebar"] > div {{
            padding-top: 1.25rem !important;
        }}
        div[data-testid="stSidebar"] div[role="radiogroup"] {{
            gap: 2px !important;
        }}
        div[data-testid="stSidebar"] div[role="radiogroup"] label {{
            font-family: 'Outfit', sans-serif !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            padding: 0.55rem 0.75rem !important;
            border-radius: 10px !important;
            margin: 1px 0 !important;
            transition: background 0.15s ease, color 0.15s ease !important;
            color: {t["text_secondary"]} !important;
        }}
        div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            background: {t["surface"]} !important;
            color: {t["text_primary"]} !important;
        }}
        div[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
        div[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
            background: {t["accent_soft"]} !important;
            color: {t["accent"]} !important;
        }}

        .sidebar-user {{
            background: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 12px;
            padding: 0.65rem 0.85rem;
            margin: 0.75rem 0 1rem 0;
        }}
        .sidebar-user-label {{
            font-size: 0.7rem;
            color: {t["text_muted"]};
            letter-spacing: 0.04em;
            text-transform: uppercase;
            display: block;
            margin-bottom: 0.15rem;
        }}
        .sidebar-user-name {{
            font-family: 'Outfit', sans-serif;
            font-size: 0.95rem;
            font-weight: 600;
            color: {t["text_primary"]};
        }}

        /* ── Widgets ── */
        .stButton>button, .stDownloadButton>button, .stFormSubmitButton>button {{
            background: {t["accent"]} !important;
            color: white !important;
            border: none !important;
            border-radius: 11px !important;
            font-weight: 600 !important;
            font-family: 'Outfit', sans-serif !important;
            font-size: 0.9rem !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
            box-shadow: 0 2px 12px rgba(124,142,245,0.25) !important;
        }}
        .stButton>button:hover, .stDownloadButton>button:hover, .stFormSubmitButton>button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 18px rgba(124,142,245,0.32) !important;
            filter: brightness(1.05);
        }}
        .stButton>button[kind="secondary"],
        .stButton>button[data-testid="stBaseButton-secondary"] {{
            background: {t["surface"]} !important;
            color: {t["text_secondary"]} !important;
            border: 1px solid {t["border"]} !important;
            box-shadow: none !important;
        }}
        .stButton>button[kind="secondary"]:hover,
        .stButton>button[data-testid="stBaseButton-secondary"]:hover {{
            background: {t["surface_hover"]} !important;
            color: {t["text_primary"]} !important;
            border-color: {t["border_strong"]} !important;
            transform: none !important;
            filter: none !important;
        }}

        div[data-baseweb="segmented-control"] {{
            background: {t["surface"]} !important;
            border: 1px solid {t["border"]} !important;
            border-radius: 12px !important;
            padding: 3px !important;
        }}
        div[data-baseweb="segmented-control"] button {{
            border-radius: 9px !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.84rem !important;
            color: {t["text_secondary"]} !important;
        }}
        div[data-baseweb="segmented-control"] button[aria-checked="true"] {{
            background: {t["accent_soft"]} !important;
            color: {t["accent"]} !important;
            box-shadow: inset 0 0 0 1px rgba(124,142,245,0.25) !important;
        }}

        div[role="radiogroup"] label {{ color: {t["text_primary"]} !important; }}

        [data-testid="stMetricValue"] {{
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            color: {t["text_primary"]} !important;
        }}

        details > summary {{
            font-family: 'Outfit', sans-serif !important;
            font-weight: 500 !important;
            border-radius: 12px !important;
        }}
        details {{
            background: {t["surface"]} !important;
            border: 1px solid {t["border"]} !important;
            border-radius: 14px !important;
            overflow: hidden;
        }}

        button[data-baseweb="tab"] {{
            font-family: 'Outfit', sans-serif !important;
            font-weight: 500 !important;
            color: {t["text_secondary"]} !important;
        }}
        button[aria-selected="true"][data-baseweb="tab"] {{
            color: {t["accent"]} !important;
            border-bottom: 2px solid {t["accent"]} !important;
        }}

        input, textarea, select {{
            background: {t["input_bg"]} !important;
            border-color: {t["border"]} !important;
            color: {t["text_primary"]} !important;
            border-radius: 11px !important;
        }}
        div[data-baseweb="select"] > div {{
            background: {t["input_bg"]} !important;
            border-color: {t["border"]} !important;
            border-radius: 11px !important;
        }}

        hr {{ border-color: {t["border"]} !important; margin: 1rem 0 !important; }}

        /* Dataframes */
        [data-testid="stDataFrame"] {{
            border: 1px solid {t["border"]};
            border-radius: 14px;
            overflow: hidden;
        }}

        /* Toggle */
        [data-testid="stSidebar"] .stCheckbox, [data-testid="stSidebar"] label {{
            font-size: 0.85rem !important;
            color: {t["text_secondary"]} !important;
        }}

        h3, h4, .stSubheader {{
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return t


def login_brand_html() -> str:
    return """
    <div style="margin-bottom: 1.75rem;">
        <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:0.5rem;">
            <span style="font-family:'Outfit',sans-serif; font-size:2.6rem; font-weight:700;
                         letter-spacing:-0.04em; line-height:1; color:#ECEEF2;">JVC</span>
            <span style="font-family:'Outfit',sans-serif; font-size:0.72rem; font-weight:500;
                         letter-spacing:0.08em; text-transform:uppercase; color:#7C8EF5;
                         padding-bottom:4px;">Team Hub</span>
        </div>
        <p style="margin:0; font-size:0.92rem; color:#8B95A8; line-height:1.5;">
            Sign in to check attendance, view stats, and manage your season.
        </p>
    </div>
    """


def login_footer_html() -> str:
    return """
    <div style="margin-top:1.25rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,0.07);
                display:flex; align-items:center; gap:8px;">
        <span style="width:6px; height:6px; background:#5CB88A; border-radius:50%; flex-shrink:0;"></span>
        <span style="color:#5C6578; font-size:0.78rem;">Encrypted session</span>
    </div>
    """


def sidebar_brand_html() -> str:
    return """
    <div style="padding:0 0 0.25rem 0;">
        <span style="font-family:'Outfit',sans-serif; font-size:1.65rem; font-weight:700;
                     color:inherit; letter-spacing:-0.03em; line-height:1;">JVC</span>
        <span style="display:block; font-size:0.68rem; font-weight:500; letter-spacing:0.1em;
                     text-transform:uppercase; color:#7C8EF5; margin-top:2px;">Team Hub</span>
    </div>
    """


def sidebar_user_html(name: str) -> str:
    return f"""
    <div class="sidebar-user">
        <span class="sidebar-user-label">Signed in</span>
        <span class="sidebar-user-name">{name}</span>
    </div>
    """
