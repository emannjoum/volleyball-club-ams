import streamlit as st
import database as db
import views

SHOW_PAYMENT_HISTORY_REPORT = False

st.set_page_config(page_title="JVC // Team Hub", layout="wide", page_icon="🏐")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role      = None
    st.session_state.user_name = None

#  LOGIN PAGE
if not st.session_state.logged_in:
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
                background-color: #05080E !important;
            }

            /* Hide default Streamlit chrome */
            #MainMenu, footer, header { visibility: hidden; }
            .block-container {
                padding-top: 4rem !important;
                max-width: 600px !important;
            }

            /* --- Main Card Styling --- */
            [data-testid="column"]:nth-of-type(2) {
                background-color: #0B0E14;
                border: 1px solid #1E293B;
                border-radius: 12px;
                padding: 2.5rem 2rem;
                box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            }

            /* --- Tab Segmented Control Overrides --- */
            div[data-baseweb="tab-list"] {
                background-color: #121620;
                border-radius: 8px;
                border: 1px solid #1E293B;
                padding: 0;
                gap: 0;
                margin-bottom: 1.5rem;
            }
            div[data-baseweb="tab-highlight"] {
                display: none !important; /* Hide native underline */
            }
            button[data-baseweb="tab"] {
                flex: 1;
                justify-content: center;
                background-color: transparent !important;
                border-radius: 8px !important;
                margin: 0 !important;
                padding: 0.9rem 1rem !important;
                border: 1px solid transparent !important;
                color: #475569 !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: 700 !important;
                letter-spacing: 0.05em !important;
                font-size: 0.9rem !important;
            }
            button[aria-selected="true"][data-baseweb="tab"] {
                background-color: #5B58F5 !important;
                color: white !important;
                border: 1px solid white !important;
            }

            /* --- Form Labels --- */
            .stSelectbox label p, .stTextInput label p {
                color: #475569 !important;
                font-size: 0.85rem !important;
                font-weight: 800 !important;
                letter-spacing: 0.05em !important;
                text-transform: uppercase !important;
                margin-bottom: 0.2rem !important;
            }

            /* --- Form Inputs --- */
            div[data-baseweb="select"] > div, input[type="password"] {
                background-color: #0B0E14 !important;
                border: 1px solid #1E293B !important;
                border-radius: 8px !important;
                color: white !important;
                padding: 0.3rem !important;
            }
            
            /* Add some spacing below selectbox */
            .stSelectbox {
                margin-bottom: 0.5rem !important;
            }

            /* --- Primary Button --- */
            .stButton > button {
                background: #5B58F5 !important;
                color: white !important;
                width: 100% !important;
                border-radius: 8px !important;
                padding: 0.8rem !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: 700 !important;
                letter-spacing: 0.05em !important;
                border: none !important;
                margin-top: 0.5rem !important;
                box-shadow: 0 4px 20px rgba(91, 88, 245, 0.25) !important;
                transition: all 0.2s ease;
            }
            .stButton > button:hover {
                background: #4F4CE5 !important;
                transform: translateY(-2px);
            }
            .stButton > button p {
                font-size: 0.9rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.1, 2, 0.1])
    
    with col2:
        # HTML Logo 
        st.markdown("""
            <div style="display: flex; flex-direction: column; margin-bottom: 2rem;">
                <div style="display: flex; align-items: flex-end; gap: 15px;">
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 4rem; font-weight: 800; line-height: 0.85; letter-spacing: -0.04em;">
                        <span style="color: #FFFFFF;">JV</span><span style="color: #6B7AFF;">C</span>
                    </div>
                    <div style="flex-grow: 1; height: 2px; background: linear-gradient(90deg, #6B7AFF 0%, transparent 100%); margin-bottom: 8px;"></div>
                </div>
                <div style="font-family: 'Inter', sans-serif; font-size: 0.85rem; font-weight: 800; color: #6B7AFF; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 15px;">
                    TEAM HUB PORTAL
                </div>
            </div>
        """, unsafe_allow_html=True)

        login_tab1, login_tab2 = st.tabs(["PLAYER", "COACH"])

        with login_tab1:
            players_list = db.load_players() if hasattr(db, 'load_players') else ["Jordan K.", "Alex M.", "Sarah T."]
            if not players_list:
                st.warning("No players found in the system.")
            else:
                sel_player = st.selectbox("SELECT PROFILE", players_list)
                
                pin_col1, pin_col2 = st.columns([3, 1])
                with pin_col1:
                    player_pin = st.text_input("ACCESS PIN", type="password")
                with pin_col2:
                    # Empty disabled-looking box for aesthetics lol sorry
                    st.text_input(" ", disabled=True, label_visibility="hidden")
                
                if st.button("AUTHORIZE ACCESS", use_container_width=True):
                    if db.verify_player_pin(sel_player, player_pin):
                        st.session_state.logged_in = True
                        st.session_state.role      = "Player"
                        st.session_state.user_name = sel_player
                        st.rerun()
                    else:
                        st.error("Incorrect PIN. Please try again.")

        with login_tab2:
            admin_pw = st.text_input("COACH PASSWORD", type="password")
            if st.button("AUTHORIZE ACCESS", key="coach_btn", use_container_width=True):
                target_pw = st.secrets.get(
                    "coach_password",
                    st.secrets.connections.supabase.get("coach_password", "coach123") if hasattr(st, 'secrets') else "coach123"
                )
                if admin_pw == target_pw:
                    st.session_state.logged_in = True
                    st.session_state.role      = "Coach"
                    st.session_state.user_name = "Coach"
                    st.rerun()
                else:
                    st.error("Invalid coach credentials.")
        
        # Secure Session Footer
        st.markdown("""
            <div style="margin-top: 1.5rem; border-top: 1px solid #1E293B; padding-top: 1.2rem; display: flex; align-items: center; gap: 8px;">
                <div style="width: 10px; height: 10px; background-color: #059669; border-radius: 50%;"></div>
                <span style="color: #475569; font-family: 'Inter', sans-serif; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em;">SECURE SESSION • JVC TEAM HUB</span>
            </div>
        """, unsafe_allow_html=True)

    st.stop()


# SIDEBAR AND LOGGED-IN VIEW 
with st.sidebar:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&display=swap');
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0A0F1E 0%, #080C14 100%) !important;
            border-right: 1px solid rgba(99,102,241,0.15) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Logo / brand
    st.markdown("""
        <div style='display:flex; flex-direction:column; align-items:flex-start; padding: 0.5rem 0 0.8rem 0;'>
            <span style='font-family:"Space Grotesk",sans-serif; font-size:2rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.03em; line-height:1;'>JVC</span>
            <span style='font-size:0.65rem; font-weight:600; letter-spacing:0.16em; text-transform:uppercase; color:#6366F1;'>TEAM HUB</span>
        </div>
    """, unsafe_allow_html=True)

    try:
        st.image("jvc_logo_trans.png", width=160)
    except Exception:
        pass

    st.markdown(f"""
        <div style='background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
             border-radius:8px; padding:0.5rem 0.75rem; margin:0.5rem 0 0.75rem 0;'>
            <span style='font-size:0.7rem; color:#64748B; text-transform:uppercase; letter-spacing:0.1em;'>Signed in as</span><br>
            <span style='font-size:0.95rem; font-weight:600; color:#E2E8F0;'>{st.session_state.user_name}</span>
        </div>
    """, unsafe_allow_html=True)

    light_mode = st.toggle("Light Mode", value=False)

    st.divider()

    if st.session_state.role == "Coach":
        nav = st.radio("Navigation", ["Admin", "Finances", "Session Manager"], label_visibility="collapsed")
    else:
        nav = st.radio("Navigation", ["Dashboard", "My Stats"], label_visibility="collapsed")
        current_user = st.session_state.user_name

    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.divider()
    if st.button("← Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()


if light_mode:
    card_bg          = "#F1F5F9"
    text_primary     = "#0F172A"
    text_secondary   = "#64748B"
    radar_label_color = "#0F172A"
    grid_empty       = "#CBD5E1"
    scroll_thumb     = "#CBD5E1"
    scroll_track     = "#F1F5F9"
    border_color     = "rgba(0,0,0,0.08)"
    panel_bg         = "#FFFFFF"
    page_bg          = "#F8FAFC"
else:
    card_bg          = "#0F1629"
    text_primary     = "#F1F5F9"
    text_secondary   = "#64748B"
    radar_label_color = "#E2E8F0"
    grid_empty       = "#1E293B"
    scroll_thumb     = "#334155"
    scroll_track     = "#0F1629"
    border_color     = "rgba(99,102,241,0.15)"
    panel_bg         = "#0F1629"
    page_bg          = "#080C14"


#  GLOBAL CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    /* ── Reset & Base ── */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: {page_bg} !important;
        color: {text_primary} !important;
    }}
    #MainMenu, footer {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.5rem !important; max-width: 1200px !important; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {scroll_track}; }}
    ::-webkit-scrollbar-thumb {{ background: {scroll_thumb}; border-radius: 3px; }}

    /* ── Page Hero ── */
    .page-hero {{
        margin-bottom: 1.8rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {border_color};
    }}
    .hero-eyebrow {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #6366F1;
        display: block;
        margin-bottom: 0.3rem;
    }}
    .hero-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.8rem, 4vw, 2.8rem);
        font-weight: 800;
        color: {text_primary};
        line-height: 1.1;
        letter-spacing: -0.02em;
        margin: 0;
    }}
    .hero-accent {{
        color: #6366F1;
    }}

    /* ── Section Headers ── */
    .section-header {{ margin: 0.5rem 0 0.8rem 0; }}
    .section-eyebrow {{
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #F59E0B;
        display: block;
        margin-bottom: 0.2rem;
    }}
    .section-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: {text_primary};
        margin: 0;
        letter-spacing: -0.01em;
    }}

    /* ── Stat Cards ── */
    .stat-card {{
        position: relative;
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.1rem 1.2rem 1rem 1.2rem;
        margin-bottom: 0.8rem;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .stat-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }}
    .card-accent {{
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 12px 12px 0 0;
    }}
    .card-label {{
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.16em !important;
        text-transform: uppercase !important;
        color: {text_secondary} !important;
        margin: 0.2rem 0 0.35rem 0 !important;
    }}
    .card-value {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        letter-spacing: -0.02em !important;
    }}
    .card-sub {{
        font-size: 0.75rem;
        color: {text_secondary};
    }}

    /* ── Helper Text ── */
    .helper-text {{
        font-size: 0.85rem;
        color: {text_secondary};
        margin: 0.3rem 0 0.8rem 0;
    }}

    /* ── Status Badges ── */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        margin-bottom: 0.8rem;
    }}
    .status-in {{
        background: rgba(16,185,129,0.12);
        color: #10B981;
        border: 1px solid rgba(16,185,129,0.25);
    }}
    .status-out {{
        background: rgba(239,68,68,0.1);
        color: #EF4444;
        border: 1px solid rgba(239,68,68,0.2);
    }}

    /* ── Pulse dot ── */
    .pulse-dot {{
        display: inline-block;
        width: 8px; height: 8px;
        background: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(16,185,129,0.6);
        animation: pulse-anim 2s infinite;
    }}
    @keyframes pulse-anim {{
        0%   {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.6); }}
        70%  {{ box-shadow: 0 0 0 7px rgba(16,185,129,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0); }}
    }}

    /* ── Streak List ── */
    .streak-list {{ display: flex; flex-direction: column; gap: 8px; }}
    .streak-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 0.55rem 0.85rem;
        transition: transform 0.15s ease;
    }}
    .streak-row:hover {{ transform: scale(1.01); }}
    .streak-rank {{ font-size: 1rem; width: 24px; text-align: center; flex-shrink: 0; }}
    .streak-info {{ flex: 1; min-width: 0; }}
    .streak-name {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {text_primary};
        display: block;
        margin-bottom: 4px;
    }}
    .streak-bar-wrap {{
        height: 6px;
        background: {grid_empty};
        border-radius: 999px;
        overflow: hidden;
    }}
    .streak-bar {{
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #6366F1, #818CF8);
        background-size: 200% 100%;
        animation: shimmer-bar 2.5s linear infinite;
    }}
    @keyframes shimmer-bar {{
        0%   {{ background-position: 100% 0; }}
        100% {{ background-position: -100% 0; }}
    }}
    .streak-count {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 800;
        color: #6366F1;
        width: 28px;
        text-align: right;
        flex-shrink: 0;
    }}

    /* ── Skill Breakdown ── */
    .skill-breakdown {{ display: flex; flex-direction: column; gap: 8px; margin-top: 0.5rem; }}
    .skill-row {{ display: flex; align-items: center; gap: 10px; }}
    .skill-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {text_secondary};
        width: 60px;
        flex-shrink: 0;
    }}
    .skill-bar-wrap {{
        flex: 1;
        height: 7px;
        background: {grid_empty};
        border-radius: 999px;
        overflow: hidden;
    }}
    .skill-bar-fill {{
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #6366F1 0%, #F59E0B 100%);
        transition: width 0.6s ease;
    }}
    .skill-num {{
        font-size: 0.78rem;
        font-weight: 700;
        color: {text_secondary};
        width: 28px;
        text-align: right;
    }}

    /* ── Activity Grid ── */
    .activity-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        padding: 0.75rem 0;
    }}
    .activity-square {{
        width: 18px; height: 18px;
        border-radius: 4px;
        cursor: crosshair;
        transition: transform 0.12s ease;
    }}
    .activity-square:hover {{ transform: scale(1.5); }}

    /* ── Player Pills ── */
    .player-pill-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 0.5rem 0;
    }}
    .player-pill {{
        background: rgba(99,102,241,0.12);
        color: #818CF8;
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 999px;
        padding: 0.2rem 0.7rem;
        font-size: 0.8rem;
        font-weight: 600;
    }}

    /* ── Session Chips ── */
    .session-chip {{
        display: inline-block;
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 0.45rem 0.9rem;
        font-size: 0.88rem;
        font-weight: 600;
        color: {text_primary};
        margin: 2px 0;
    }}
    .cancelled-chip {{
        background: rgba(239,68,68,0.07);
        border-color: rgba(239,68,68,0.2);
        color: #F87171;
        text-decoration: line-through;
    }}

    /* ── Info Bar ── */
    .info-bar {{
        background: rgba(99,102,241,0.07);
        border: 1px solid rgba(99,102,241,0.18);
        border-radius: 8px;
        padding: 0.55rem 1rem;
        font-size: 0.82rem;
        color: {text_secondary};
        margin-bottom: 1rem;
    }}
    .info-bar b {{ color: #818CF8; }}

    /* ── Streamlit Widget Overrides ── */
    .stButton>button, .stDownloadButton>button {{
        background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
    }}
    .stButton>button:hover, .stDownloadButton>button:hover {{
        background: linear-gradient(135deg, #4F46E5, #4338CA) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important;
    }}

    div[data-baseweb="segmented-control"] button[aria-checked="true"] {{
        background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
        color: white !important;
        border-radius: 6px !important;
    }}

    div[role="radiogroup"] label {{
        color: {text_primary} !important;
    }}

    /* Sidebar radio items */
    div[data-testid="stSidebar"] div[role="radiogroup"] label {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: 0.4rem 0 !important;
        transition: color 0.15s ease !important;
    }}
    div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        color: #6366F1 !important;
    }}

    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 800 !important;
        color: {text_primary} !important;
    }}

    /* Expanders */
    details > summary {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
    }}

    /* Tabs */
    button[data-baseweb="tab"] {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
    }}
    button[aria-selected="true"][data-baseweb="tab"] {{
        color: #6366F1 !important;
        border-bottom: 2px solid #6366F1 !important;
    }}

    /* Inputs */
    input, textarea, select {{
        background: {card_bg} !important;
        border-color: {border_color} !important;
        color: {text_primary} !important;
        border-radius: 8px !important;
    }}

    /* Divider */
    hr {{ border-color: {border_color} !important; }}

    /* Selectbox / number input */
    div[data-baseweb="select"] > div {{
        background: {card_bg} !important;
        border-color: {border_color} !important;
        border-radius: 8px !important;
    }}
    </style>
""", unsafe_allow_html=True)


if nav == "Dashboard" and st.session_state.role == "Player":
    views.render_player_dashboard(current_user, radar_label_color)
elif nav == "My Stats" and st.session_state.role == "Player":
    views.render_player_stats(current_user, grid_empty)
elif nav == "Admin" and st.session_state.role == "Coach":
    views.render_admin()
elif nav == "Finances" and st.session_state.role == "Coach":
    views.render_finances(SHOW_PAYMENT_HISTORY_REPORT)
elif nav == "Session Manager" and st.session_state.role == "Coach":
    views.render_session_manager()