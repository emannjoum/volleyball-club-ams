import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import random

SHOW_PAYMENT_HISTORY_REPORT = False 

st.set_page_config(page_title="JVC // Team Hub", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .brand-text { font-weight: 800; font-size: 2.2rem; color: #059669; }
    
    .stButton>button, .stDownloadButton>button {
        background-color: #059669 !important;
        color: white !important;
        border: none !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #047857 !important;
    }
    
    div[data-baseweb="segmented-control"] button[aria-checked="true"] {
        background-color: #059669 !important;
        color: white !important;
    }
    div[role="radiogroup"] label > div:first-child[data-checked="true"] {
        background-color: #059669 !important;
        border-color: #059669 !important;
    }
    
    /* Custom Styling for Player Metric Cards */
    .metric-card {
        background-color: #f8fafc;
        border-left: 4px solid #059669;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# SESSION STATE INITIALIZATION 
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_name = None

conn = st.connection(
    "supabase", 
    type=SupabaseConnection,
    url=st.secrets.connections.supabase.url, 
    key=st.secrets.connections.supabase.key
)

# DATABASE & LOGIC FUNCTIONS 

def get_next_session_date():
    """Calculates the date of the next Sunday (6) or Thursday (3)."""
    today = datetime.now()
    days_ahead = 0
    while True:
        candidate = today + timedelta(days=days_ahead)
        # Python weekday(): Monday is 0, Thursday is 3, Sunday is 6
        if candidate.weekday() in [3, 6]:
            return candidate.strftime("%b %d")
        days_ahead += 1

def load_players():
    try:
        query = conn.table("players").select("name").order("name").execute()
        if query.data:
            return [row["name"] for row in query.data]
        return []
    except Exception as e:
        st.error(f"Error loading players: {e}")
        return []

def get_roster_with_pins():
    try:
        query = conn.table("players").select("name, position, access_code").order("name").execute()
        if query.data: return pd.DataFrame(query.data)
        return pd.DataFrame(columns=["name", "position", "access_code"])
    except:
        return pd.DataFrame(columns=["name", "position", "access_code"])

def verify_player_pin(name, pin):
    try:
        query = conn.table("players").select("access_code").eq("name", name).execute()
        if query.data and query.data[0]["access_code"] == pin:
            return True
        return False
    except:
        return False

def add_player(name, position):
    pin = str(random.randint(1000, 9999))
    try:
        conn.table("players").insert({"name": name, "position": position, "access_code": pin}).execute()
        conn.table("player_credits").insert({"player": name, "remaining_sessions": 0}).execute()
        return pin 
    except Exception as e:
        st.error(f"Error adding player: {e}")
        return None

def load_player_credits(player_name):
    try:
        query = conn.table("player_credits").select("remaining_sessions").eq("player", player_name).execute()
        if query.data: return query.data[0]["remaining_sessions"]
        return 0
    except:
        return 0

def update_player_credits(player_name, sessions_to_add, plan_type="Custom Adjustment"):
    try:
        current_sessions = load_player_credits(player_name)
        new_total = current_sessions + sessions_to_add
        conn.table("player_credits").upsert({"player": player_name, "remaining_sessions": new_total}).execute()
        
        if sessions_to_add > 0:
            conn.table("payment_history").insert({
                "player": player_name, "sessions_added": sessions_to_add, "plan_type": plan_type
            }).execute()
        return True
    except Exception as e:
        st.error(f"DB Error: {e}")
        return False

def load_payment_history():
    try:
        query = conn.table("payment_history").select("*").order("created_at", desc=True).execute()
        df = pd.DataFrame(query.data)
        if df.empty: return pd.DataFrame(columns=["created_at", "player", "plan_type", "sessions_added"])
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%b %d, %Y')
        df = df.rename(columns={"created_at": "Date", "player": "Player", "plan_type": "Payment Plan", "sessions_added": "Sessions Added"})
        return df[['Date', 'Player', 'Payment Plan', 'Sessions Added']]
    except:
        return pd.DataFrame(columns=["Date", "Player", "Payment Plan", "Sessions Added"])

def save_attendance(player_name, status):
    target_date = get_next_session_date()
    try:
        # Check against the target schedule date, not just "today"
        existing = conn.table("attendance").select("*").eq("player", player_name).eq("date", target_date).execute()
        if existing.data:
            st.warning(f"You have already submitted your status for {target_date}.")
            return False

        if status == "Available":
            current_sessions = load_player_credits(player_name)
            conn.table("player_credits").upsert({"player": player_name, "remaining_sessions": current_sessions - 1}).execute()

        conn.table("attendance").insert({"player": player_name, "status": status, "date": target_date}).execute()
        return True
    except Exception as e:
        st.error(f"DB Error: {e}")
        return False

def load_attendance():
    try:
        query = conn.table("attendance").select("*").execute()
        df = pd.DataFrame(query.data)
        if df.empty: return pd.DataFrame(columns=["date", "player", "status", "created_at"])
        return df
    except:
        return pd.DataFrame(columns=["date", "player", "status", "created_at"])

def calculate_streaks(df):
    if df.empty or 'status' not in df.columns or 'player' not in df.columns: return pd.DataFrame(columns=["Player", "Max Streak"])
    streaks = []
    for player in df['player'].unique():
        p_df = df[df['player'] == player]
        if 'created_at' in p_df.columns: p_df = p_df.sort_values('created_at')
        max_streak = 0
        current_streak = 0
        for status in p_df['status']:
            if status == "Available":
                current_streak += 1
                if current_streak > max_streak: max_streak = current_streak
            else:
                current_streak = 0
        streaks.append({"Player": player, "Max Streak": max_streak})
    return pd.DataFrame(streaks).sort_values(by="Max Streak", ascending=False).reset_index(drop=True)

def save_stats(player_name, h, s, p, sv, d):
    try:
        data = {"player": player_name, "hitting": h, "setting": s, "passing": p, "serving": sv, "defense": d}
        conn.table("player_stats").upsert(data, on_conflict="player").execute()
        return True
    except:
        return False

def load_player_stats(player_name):
    try:
        query = conn.table("player_stats").select("*").eq("player", player_name).execute()
        if query.data: return query.data[0]
        return {"hitting": 3, "setting": 3, "passing": 3, "serving": 3, "defense": 3}
    except:
        return {"hitting": 3, "setting": 3, "passing": 3, "serving": 3, "defense": 3}

def create_pdf(df, title="JVC Attendance Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    data = [df.columns.to_list()] + df.values.tolist()
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#059669")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#f1f5f9")]),
    ]))
    elements.append(t)
    doc.build(elements)
    return buffer.getvalue()


if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.image("jvc_logo_trans.png", use_container_width=True)
        st.markdown("<h2 style='text-align: center; color: #059669;'>JVC Team Hub Portal</h2>", unsafe_allow_html=True)
        
        login_tab1, login_tab2 = st.tabs(["Player Login", "Coach Login"])
        
        with login_tab1:
            players_list = load_players()
            if not players_list:
                st.warning("No players found in database.")
            else:
                sel_player = st.selectbox("Select Your Profile", players_list)
                player_pin = st.text_input("Enter 4-Digit PIN", type="password")
                if st.button("Enter Gym", use_container_width=True):
                    if verify_player_pin(sel_player, player_pin):
                        st.session_state.logged_in = True
                        st.session_state.role = "Player"
                        st.session_state.user_name = sel_player
                        st.rerun()
                    else:
                        st.error("Incorrect PIN.")
                        
        with login_tab2:
            admin_pw = st.text_input("Coach Password", type="password")
            target_pw = st.secrets.get("coach_password", "coach123") 
            if st.button("Access Headquarters", use_container_width=True):
                if admin_pw == target_pw:
                    st.session_state.logged_in = True
                    st.session_state.role = "Coach"
                    st.session_state.user_name = "Coach"
                    st.rerun()
                else:
                    st.error("Access Denied.")
    st.stop()


# SIDEBAR ::::::::::::::::::::::
with st.sidebar:
    st.markdown(
        """
        <div style='display: flex; flex-direction: column;'>
            <h2 style='color: #059669; font-weight: 800; margin: 0; padding: 0;'>JVC</h2>
            <span style='color: #6b7280; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;'>Team Hub</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.divider()
    
    st.markdown(
        """
        <style>
        .sidebar-logo-container { display: flex; justify-content: center; align-items: center; margin-top: 2px;}
        [data-testid="stImage"] { margin-bottom: -15px; }
        hr { margin-top: 8px !important; margin-bottom: 8px !important; border-color: #e5e7eb !important; }
        </style>
        <div class='sidebar-logo-container'>
        """, 
        unsafe_allow_html=True
    )
    st.image("jvc_logo_trans.png", width=190)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"**Logged in as:** {st.session_state.user_name}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.divider()

    if st.session_state.role == "Coach":
        nav = st.radio("Menu", ["Admin", "Finances"], label_visibility="collapsed")
    else:
        nav = st.radio("Menu", ["Dashboard", "My Stats"], label_visibility="collapsed")
        current_user = st.session_state.user_name


# MAIN NAV VIEWS 

if nav == "Dashboard" and st.session_state.role == "Player":
    st.markdown(f"<h1>Locker Room: {current_user.split()[0]}</h1>", unsafe_allow_html=True)
    
    next_session = get_next_session_date()
    db_data = load_attendance()
    stats = load_player_stats(current_user)
    
    # Calculate player's top skill for the badge (maybe just player's level later? whatever the coach picks)
    skill_names = ['Hitting', 'Setting', 'Passing', 'Serving', 'Defense']
    skill_values = [stats['hitting'], stats['setting'], stats['passing'], stats['serving'], stats['defense']]
    top_skill = skill_names[skill_values.index(max(skill_values))]
    
    # TOP METRICS ROW  :::::::::::::::::::::::::::::::::::::
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #64748b; margin:0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase;'>Next Practice</p>
                <h2 style='color: #0f172a; margin:0; font-weight: 900;'>{next_session}</h2>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        current_credits = load_player_credits(current_user)
        credit_color = "#059669" if current_credits > 0 else "#dc2626"
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #64748b; margin:0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase;'>Remaining Sessions</p>
                <h2 style='color: {credit_color}; margin:0; font-weight: 900;'>{current_credits} Tickets</h2>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <p style='color: #64748b; margin:0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase;'>Coach's Rating</p>
                <h2 style='color: #0f172a; margin:0; font-weight: 900;'>Top: {top_skill}</h2>
            </div>
        """, unsafe_allow_html=True)

    # MAIN CONTENT ::::::::::::::::::::::::::::::;
    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        st.markdown(f"### Check-in for {next_session}")
        st.write("Let the coach know if you'll be on the court.")
        status = st.segmented_control("Your Status", ["Available", "Unavailable"], default="Available")
        if st.button("Submit Attendance", use_container_width=True):
            if save_attendance(current_user, status):
                st.success(f"Status locked in for {next_session}!")
                st.rerun()

        st.divider()
        
        st.markdown("### Top Players (Streaks)")
        if not db_data.empty:
            streak_df = calculate_streaks(db_data)
            st.dataframe(
                streak_df.head(5), # Only show top 5 so it doesn't clutter
                use_container_width=True, 
                hide_index=True,
                column_config={"Max Streak": st.column_config.NumberColumn("Matches in a row", alignment="right")}
            )

    with c2:
        st.markdown("### Your Skill Radar")
        df_skill = pd.DataFrame(dict(
            r=skill_values,
            theta=skill_names
        ))
        fig = px.line_polar(df_skill, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#059669', fillcolor='rgba(5, 150, 105, 0.2)')
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=14, color="black", weight="bold"))
            ), 
            showlegend=False, 
            height=350,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

elif nav == "My Stats" and st.session_state.role == "Player":
    st.markdown(f"<h2>Season History: {current_user}</h2>", unsafe_allow_html=True)
    db_data = load_attendance()
    if not db_data.empty:
        user_data = db_data[db_data['player'] == current_user]
        
        total_sessions = len(user_data)
        attended = len(user_data[user_data['status'] == 'Available'])
        attendance_rate = int((attended / total_sessions * 100)) if total_sessions > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Check-ins Logged", total_sessions)
        col2.metric("Practices Attended", attended)
        col3.metric("Attendance Rate", f"{attendance_rate}%")
        
        st.divider()
        
        selected_cols = ['date', 'status'] 
        def highlight_attendance(val):
            if val == 'Available': return 'color: #166534; font-weight: bold'
            if val == 'Unavailable': return 'color: #991b1b'
            return ''
        
        st.dataframe(
            user_data[selected_cols].style.map(highlight_attendance, subset=['status']) if hasattr(user_data[selected_cols].style, 'map') else user_data[selected_cols].style.applymap(highlight_attendance, subset=['status']), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("No attendance records found.")

elif nav == "Admin" and st.session_state.role == "Coach":
    st.markdown("<h1 class='brand-text'>Coach Admin</h1>", unsafe_allow_html=True)
    
    # Check for the next upcoming session using the new function
    upcoming_date = get_next_session_date()
    db_data = load_attendance()
    
    if not db_data.empty:
        upcoming_data = db_data[db_data['date'] == upcoming_date]
        available_players = upcoming_data[upcoming_data['status'] == 'Available']['player'].tolist()
        
        st.markdown(f"### Upcoming Session: {upcoming_date}")
        col_count, col_names = st.columns([1, 4])
        with col_count:
            st.metric("Total Attending", len(available_players))
        with col_names:
            if available_players:
                st.write("**Confirmed Players:**")
                st.write(", ".join(available_players))
            else:
                st.write("**Confirmed Players:**\nNo players confirmed yet.")
        st.divider()

    tab1, tab2, tab3 = st.tabs(["Attendance & PDF", "Insert Player Stats", "Manage Roster"])
    
    with tab1:
        if not db_data.empty:
            st.download_button("Generate Attendance PDF", data=create_pdf(db_data, "JVC Attendance Report"), file_name="attendance.pdf", mime="application/pdf")
            pivot_df = db_data.pivot_table(index='player', columns='date', values='status', aggfunc='first').fillna("Unavailable")
            
            def color_matrix(val):
                if val == 'Available': return 'background-color: #bbf7d0; color: #166534'
                elif val == 'Unavailable': return 'background-color: #fecaca; color: #991b1b'
                return ''
            
            styled_df = pivot_df.style.map(color_matrix) if hasattr(pivot_df.style, 'map') else pivot_df.style.applymap(color_matrix)
            st.dataframe(styled_df, use_container_width=True)

    with tab2:
        players_list = load_players()
        if players_list:
            target = st.selectbox("Select Player", players_list)
            cur = load_player_stats(target)
            col1, col2 = st.columns(2)
            with col1:
                h = st.slider("Hitting", 1, 5, int(cur['hitting']))
                s = st.slider("Setting", 1, 5, int(cur['setting']))
                p = st.slider("Passing", 1, 5, int(cur['passing']))
            with col2:
                sv = st.slider("Serving", 1, 5, int(cur['serving']))
                d = st.slider("Defense", 1, 5, int(cur['defense']))
            if st.button("Update Stats"):
                if save_stats(target, h, s, p, sv, d): st.success("Updated")
        else:
            st.info("Add players in the Manage Roster tab first.")

    with tab3:
        st.subheader("Add New Player")
        with st.form("new_player_form"):
            new_name = st.text_input("Full Name / Display Name")
            new_pos = st.selectbox("Position", ["None", "Outside Hitter", "Middle Blocker", "Setter", "Libero", "Opposite", "Defensive Specialist"])

            submitted = st.form_submit_button("Create Profile")
            if submitted:
                if new_name:
                    pin = add_player(new_name, new_pos)
                    if pin:
                        st.success(f"Added **{new_name}**! Their login PIN is: **{pin}**")
                else:
                    st.error("Player name is required.")
                    
        st.divider()
        st.subheader("Current Roster & Login PINs")
        roster_df = get_roster_with_pins()
        if not roster_df.empty:
            roster_df = roster_df.rename(columns={"name": "Player", "position": "Position", "access_code": "Login PIN"})
            st.dataframe(roster_df, use_container_width=True, hide_index=True)

elif nav == "Finances" and st.session_state.role == "Coach":
    st.markdown("<h1 class='brand-text'>Financial HQ</h1>", unsafe_allow_html=True)
    st.write("Manage player payments and see who is covered for today's session.")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    players_list = load_players()
    
    with col1:
        st.subheader("Record Payment")
        if players_list:
            with st.form("payment_form"):
                target_player = st.selectbox("Select Player", players_list)
                plan_type = st.radio("Payment Plan Type", ["Monthly (8 Sessions)", "Daily (1 Session)", "Custom Amount"])
                
                custom_amount = 0
                if plan_type == "Custom Amount":
                    custom_amount = st.number_input("Enter custom amount of sessions", min_value=-50, max_value=50, value=0)
                
                if st.form_submit_button("Confirm Payment"):
                    sessions_to_add = 0
                    if plan_type == "Monthly (8 Sessions)": sessions_to_add = 8
                    elif plan_type == "Daily (1 Session)": sessions_to_add = 1
                    else: sessions_to_add = custom_amount
                        
                    if update_player_credits(target_player, sessions_to_add, plan_type):
                        st.success(f"Logged! {sessions_to_add} session(s) added to {target_player}'s account.")
                        st.rerun()
        else:
            st.info("No players available.")

    with col2:
        upcoming_date = get_next_session_date()
        st.subheader(f"Payments for {upcoming_date}")
        
        try:
            att_query = conn.table("attendance").select("player").eq("date", upcoming_date).eq("status", "Available").execute()
            if att_query.data:
                attendees = [row['player'] for row in att_query.data]
                cred_query = conn.table("player_credits").select("player, remaining_sessions").execute()
                df_creds = pd.DataFrame(cred_query.data)
                
                df_today = df_creds[df_creds['player'].isin(attendees)].copy()
                df_today['Payment Status'] = df_today['remaining_sessions'].apply(lambda x: "Paid" if x >= 0 else "-")
                df_today = df_today[['player', 'Payment Status']].rename(columns={"player": "Player"})
                
                def highlight_status(val):
                    if val == 'Paid': return 'background-color: #bbf7d0; color: #166534; font-weight: 500'
                    if val == '-': return 'background-color: #fca5a5; color: #991b1b; font-weight: 800; text-align: center'
                    return ''
                    
                st.dataframe(
                    df_today.style.map(highlight_status, subset=['Payment Status']) if hasattr(df_today.style, 'map') else df_today.style.applymap(highlight_status, subset=['Payment Status']),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(f"No players have checked in for {upcoming_date} yet.")
        except Exception as e:
            st.error("Could not load payment data.")
            
    st.divider()

    st.subheader("Reports & Export")
    if SHOW_PAYMENT_HISTORY_REPORT:
        rep_col1, rep_col2 = st.columns(2, gap="large")
    else:
        rep_col1, rep_col2 = st.columns([1, 1]) 
        
    with rep_col1:
        st.markdown("### Debt Report")
        query = conn.table("player_credits").select("player, remaining_sessions").lte("remaining_sessions", 0).order("remaining_sessions").execute()
        if query.data:
            df_debt = pd.DataFrame(query.data)
            df_debt = df_debt.rename(columns={"player": "Player", "remaining_sessions": "Sessions Owed"})
            df_debt["Sessions Owed"] = df_debt["Sessions Owed"].abs() 
            st.dataframe(df_debt, use_container_width=True, hide_index=True)
            
            st.download_button(
                label="⬇Download Debt Report (PDF)", 
                data=create_pdf(df_debt, "JVC - Players In Debt Report"), 
                file_name=f"JVC_Debt_Report_{datetime.now().strftime('%b_%d')}.pdf", 
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.success("Everyone is paid up")
            
    if SHOW_PAYMENT_HISTORY_REPORT:
        with rep_col2:
            st.markdown("### Payment History")
            df_history = load_payment_history()
            if not df_history.empty:
                st.dataframe(df_history, use_container_width=True, hide_index=True)
                st.download_button(
                    label="⬇Download Payment History (PDF)", 
                    data=create_pdf(df_history, "JVC - Payment Transaction Log"), 
                    file_name=f"JVC_Payment_History_{datetime.now().strftime('%b_%d')}.pdf", 
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("No payment transactions recorded yet.")