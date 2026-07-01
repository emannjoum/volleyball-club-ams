import streamlit as st
import database as db
import views
import ui_theme as theme

SHOW_PAYMENT_HISTORY_REPORT = False

st.set_page_config(page_title="JVC · Team Hub", layout="wide", page_icon="🏐")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role      = None
    st.session_state.user_name = None

# ── Login ────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    theme.inject_login_css()

    _, col, _ = st.columns([0.12, 1, 0.12])

    with col:
        st.markdown(theme.login_brand_html(), unsafe_allow_html=True)

        login_tab1, login_tab2 = st.tabs(["Player", "Coach"])

        with login_tab1:
            players_list = db.load_players() if hasattr(db, "load_players") else []
            if not players_list:
                st.warning("No players found in the system.")
            else:
                sel_player = st.selectbox("Profile", players_list)
                player_pin = st.text_input("Access PIN", type="password")

                if st.button("Sign in", use_container_width=True):
                    if db.verify_player_pin(sel_player, player_pin):
                        st.session_state.logged_in = True
                        st.session_state.role      = "Player"
                        st.session_state.user_name = sel_player
                        st.rerun()
                    else:
                        st.error("Incorrect PIN. Please try again.")

        with login_tab2:
            admin_pw = st.text_input("Coach password", type="password")
            if st.button("Sign in", key="coach_btn", use_container_width=True):
                target_pw = st.secrets.get(
                    "coach_password",
                    st.secrets.connections.supabase.get("coach_password", "coach123")
                    if hasattr(st, "secrets") else "coach123",
                )
                if admin_pw == target_pw:
                    st.session_state.logged_in = True
                    st.session_state.role      = "Coach"
                    st.session_state.user_name = "Coach"
                    st.rerun()
                else:
                    st.error("Invalid coach credentials.")

        st.markdown(theme.login_footer_html(), unsafe_allow_html=True)

    st.stop()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(theme.sidebar_brand_html(), unsafe_allow_html=True)

    try:
        st.image("jvc_logo_trans.png", width=140)
    except Exception:
        pass

    st.markdown(theme.sidebar_user_html(st.session_state.user_name), unsafe_allow_html=True)

    light_mode = st.toggle("Light mode", value=False)

    st.divider()

    if st.session_state.role == "Coach":
        nav = st.radio("Navigation", ["Admin", "Finances", "Session Manager"], label_visibility="collapsed")
    else:
        nav = st.radio("Navigation", ["Dashboard", "My Stats"], label_visibility="collapsed")
        current_user = st.session_state.user_name

    st.divider()
    if st.button("Sign out", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()


# ── Main app ─────────────────────────────────────────────────────────────────
t = theme.inject_global_css(light_mode)
radar_label_color = t["radar_label"]
grid_empty        = t["grid_empty"]

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
