import streamlit as st
import database as db
import views

SHOW_PAYMENT_HISTORY_REPORT = False 

st.set_page_config(page_title="JVC // Team Hub", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_name = None

if not st.session_state.logged_in:
    st.markdown("""
        <style>
            .block-container { padding-top: 2rem !important; }
            @media (min-width: 800px) { .block-container { max-width: 800px !important; } }
            @media (max-width: 799px) { .block-container { max-width: 500px !important; padding-top: 1rem !important; } }
            [data-testid="stVerticalBlock"] > div { gap: 0.8rem !important; }
            div[data-testid="stTabs"] { margin-top: 0px !important; }
            h2 { margin-top: -10px !important; font-size: clamp(1.5rem, 5vw, 2.5rem) !important; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.5, 2, 0.5]) 
    
    with col2:
        st.image("jvc_logo_trans.png", use_container_width=True)
        # CHANGED: Headline color from green to white
        st.markdown("<h2 style='text-align: center; color: #ffffff; margin-bottom: 0px;'>JVC Team Hub Portal</h2>", unsafe_allow_html=True)
        
        login_tab1, login_tab2 = st.tabs(["Player Login", "Coach Login"])
        
        with login_tab1:
            players_list = db.load_players()
            if not players_list:
                st.warning("No players found.")
            else:
                sel_player = st.selectbox("Select Your Profile", players_list)
                player_pin = st.text_input("Enter 4-Digit PIN", type="password")
                if st.button("Login", use_container_width=True):
                    if db.verify_player_pin(sel_player, player_pin):
                        st.session_state.logged_in = True
                        st.session_state.role = "Player"
                        st.session_state.user_name = sel_player
                        st.rerun()
                    else:
                        st.error("Incorrect PIN. Please try again.")

        with login_tab2:
            admin_pw = st.text_input("Coach Password", type="password")
            if st.button("Login as Coach", use_container_width=True):
                target_pw = st.secrets.get("coach_password", st.secrets.connections.supabase.get("coach_password", "coach123"))
                if admin_pw == target_pw: 
                    st.session_state.logged_in = True
                    st.session_state.role = "Coach"
                    st.session_state.user_name = "Coach"
                    st.rerun()
                else:
                    st.error("Invalid Coach Credentials.")
    st.stop()


# THEME AND SIDEBAR SETUP
with st.sidebar:
    # CHANGED: Headline color from green to white
    st.markdown("<div style='display: flex; flex-direction: column;'><h2 style='color: #ffffff; font-weight: 800; margin: 0; padding: 0;'>JVC</h2><span style='color: #6b7280; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;'>Team Hub</span></div>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("""
        <style>
        .sidebar-logo-container { display: flex; justify-content: center; align-items: center; margin-top: 2px;}
        [data-testid="stImage"] { margin-bottom: -15px; }
        hr { margin-top: 8px !important; margin-bottom: 8px !important; border-color: #e5e7eb !important; }
        </style>
        <div class='sidebar-logo-container'>
    """, unsafe_allow_html=True)
    
    st.image("jvc_logo_trans.png", width=190)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"**Logged in as:** {st.session_state.user_name}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.divider()
    
    light_mode = st.toggle("Light Mode UI", value=False)
    
    if st.session_state.role == "Coach":
        nav = st.radio("Menu", ["Admin", "Finances"], label_visibility="collapsed")
    else:
        nav = st.radio("Menu", ["Dashboard", "My Stats"], label_visibility="collapsed")
        current_user = st.session_state.user_name


if light_mode:
    card_bg = "#f8fafc"
    text_primary = "#0f172a"
    text_secondary = "#64748b"
    radar_label_color = "#0f172a"
    grid_empty = "#e2e8f0"
    scroll_thumb = "#cbd5e1"
    scroll_thumb_hover = "#94a3b8"
    shadow_color = "rgba(0, 0, 0, 0.1)"
else:
    card_bg = "#1e293b"
    text_primary = "#f1f5f9"
    text_secondary = "#94a3b8"
    radar_label_color = "#f1f5f9"
    grid_empty = "#334155"
    scroll_thumb = "#475569"
    scroll_thumb_hover = "#64748b"
    shadow_color = "rgba(0, 0, 0, 0.4)"

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    /* CHANGED: brand-text color from green to white */
    .brand-text {{ font-weight: 800; font-size: 2.2rem; color: #ffffff; }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {scroll_thumb}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {scroll_thumb_hover}; }}
    
    .stButton>button, .stDownloadButton>button {{ background-color: #059669 !important; color: white !important; border: none !important; }}
    .stButton>button:hover, .stDownloadButton>button:hover {{ background-color: #047857 !important; }}
    div[data-baseweb="segmented-control"] button[aria-checked="true"] {{ background-color: #059669 !important; color: white !important; }}
    div[role="radiogroup"] label > div:first-child[data-checked="true"] {{ background-color: #059669 !important; border-color: #059669 !important; }}
    
    /* CHANGED: Gradient Typography from green to white/silver */
    .gradient-text {{
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        margin-bottom: 15px;
    }}
    
    /* Interactive Metric Cards */
    .metric-card {{ 
        background-color: {card_bg}; 
        border-left: 4px solid #059669; 
        padding: 1rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        transition: all 0.3s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px {shadow_color}, 0 4px 6px -2px {shadow_color};
    }}
    .metric-card p {{ color: {text_secondary} !important; }}
    .metric-card h2 {{ color: {text_primary} !important; }}
    
    /* Animated Candy Stripe Progress */
    .animated-progress {{ width: 100%; background-color: {grid_empty}; border-radius: 999px; overflow: hidden; height: 14px; margin-top: 2px; }}
    .animated-progress-bar {{ height: 100%; background: repeating-linear-gradient(45deg, #059669, #059669 10px, #10b981 10px, #10b981 20px); background-size: 28px 28px; animation: move-stripes 1s linear infinite; border-radius: 999px; transition: width 0.5s ease; }}
    @keyframes move-stripes {{ 0% {{ background-position: 0 0; }} 100% {{ background-position: 28px 0; }} }}
    
    .streak-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; background-color: {card_bg}; border-radius: 6px; margin-bottom: 8px; transition: all 0.2s ease; }}
    .streak-row:hover {{ transform: scale(1.02); }}
    .streak-name {{ font-weight: 600; width: 30%; color: {text_primary}; }}
    .streak-bar-container {{ width: 60%; padding: 0 10px; }}
    .streak-val {{ width: 10%; text-align: right; font-weight: 800; color: #059669; }}
    
    /* Pulsing Live Indicator */
    .pulse-dot {{
        display: inline-block; width: 10px; height: 10px;
        background-color: #10b981; border-radius: 50%; margin-right: 6px;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse-animation 2s infinite;
    }}
    @keyframes pulse-animation {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}
    
    /* Activity Log Hover Physics */
    .activity-square {{ transition: transform 0.15s ease, z-index 0.15s ease; cursor: crosshair; }}
    .activity-square:hover {{ transform: scale(1.4); z-index: 10; border: 1px solid #fff; }}
    
    </style>
""", unsafe_allow_html=True)

# ROUTING
if nav == "Dashboard" and st.session_state.role == "Player":
    views.render_player_dashboard(current_user, radar_label_color)
elif nav == "My Stats" and st.session_state.role == "Player":
    views.render_player_stats(current_user, grid_empty)
elif nav == "Admin" and st.session_state.role == "Coach":
    views.render_admin()
elif nav == "Finances" and st.session_state.role == "Coach":
    views.render_finances(SHOW_PAYMENT_HISTORY_REPORT)