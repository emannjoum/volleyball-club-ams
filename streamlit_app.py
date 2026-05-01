import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from st_supabase_connection import SupabaseConnection
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

conn = st.connection(
    "supabase", 
    type=SupabaseConnection,
    url=st.secrets["SUPABASE_URL"],
    key=st.secrets["SUPABASE_KEY"]
)
 
# 3 tables are used: players, attendance, and player_stats

def load_players():
    try:
        query = conn.table("players").select("name").order("name").execute()
        if query.data:
            return [row["name"] for row in query.data]
        return []
    except Exception as e:
        st.error(f"Error loading players: {e}")
        return []

def add_player(name, position): # to the players db, only coach can do
    try:
        conn.table("players").insert({
            "name": name,
            "position": position
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error adding player: {e}")
        return False

def save_attendance(player_name, status):
    try:
        conn.table("attendance").insert({
            "player": player_name,
            "status": status,
            "date": datetime.now().strftime("%b %d")
        }).execute()
        return True
    except Exception as e:
        st.error(f"DB Error: {e}")
        return False

def load_attendance():
    try:
        query = conn.table("attendance").select("*").execute()
        df = pd.DataFrame(query.data)
        if df.empty:
            return pd.DataFrame(columns=["date", "player", "status", "created_at"])
        return df
    except:
        return pd.DataFrame(columns=["date", "player", "status", "created_at"])

def calculate_streaks(df):
    if df.empty or 'status' not in df.columns or 'player' not in df.columns:
        return pd.DataFrame(columns=["Player", "Max Streak"])
    
    streaks = []
    for player in df['player'].unique():
        p_df = df[df['player'] == player]
        if 'created_at' in p_df.columns:
            p_df = p_df.sort_values('created_at')
        
        max_streak = 0
        current_streak = 0
        for status in p_df['status']:
            if status == "Available":
                current_streak += 1
                if current_streak > max_streak:
                    max_streak = current_streak
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

def create_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("JVC Attendance Report", styles['Title'])]
    data = [df.columns.to_list()] + df.values.tolist()
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#059669")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    doc.build(elements)
    return buffer.getvalue()

st.set_page_config(page_title="JVC // Team Hub", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .brand-text { font-weight: 800; font-size: 2.2rem; color: #059669; }
    
    /* Uniform Clickable Color: Emerald Green */
    .stButton>button, .stDownloadButton>button {
        background-color: #059669 !important;
        color: white !important;
        border: none !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #047857 !important;
    }
    
    /* Segmented Control and Radio Buttons Green Override */
    div[data-baseweb="segmented-control"] button[aria-checked="true"] {
        background-color: #059669 !important;
        color: white !important;
    }
    div[role="radiogroup"] label > div:first-child[data-checked="true"] {
        background-color: #059669 !important;
        border-color: #059669 !important;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 class='brand-text'>JVC</h2>", unsafe_allow_html=True)
    st.divider()
    
    players_list = load_players()
    
    if not players_list:
        st.warning("No players found. Admin must add profiles.")
        current_user = None
    else:
        current_user = st.selectbox("Active Player", players_list)
        
    nav = st.radio("Menu", ["Dashboard", "My Stats", "Admin"], label_visibility="collapsed")

# Stop rendering standard views if no players exist yet
if not current_user and nav != "Admin":
    st.stop()

if nav == "Dashboard":
    st.markdown(f"<h1>Welcome back, {current_user.split()[0]}.</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1.5], gap="large")
    with c1:
        st.markdown("### Check-in")
        status = st.segmented_control("Your Status", ["Available", "Unavailable"], default="Available")
        if st.button("Confirm Attendance", use_container_width=True):
            if save_attendance(current_user, status):
                st.toast(f"Logged for {current_user}")

    with c2:
        st.markdown("### Your Skill Profile")
        stats = load_player_stats(current_user)
        df_skill = pd.DataFrame(dict(
            r=[stats['hitting'], stats['setting'], stats['passing'], stats['serving'], stats['defense']],
            theta=['Hitting', 'Setting', 'Passing', 'Serving', 'Defense']
        ))
        fig = px.line_polar(df_skill, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#059669')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h2 class='brand-text'>Attendance Leaderboard</h2>", unsafe_allow_html=True)
    db_data = load_attendance()
    if not db_data.empty:
        streak_df = calculate_streaks(db_data)
        st.dataframe(
            streak_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={"Max Streak": st.column_config.NumberColumn("Max Streak", alignment="right")}
        )

elif nav == "Admin":
    st.markdown("<h1 class='brand-text'>Coach Admin</h1>", unsafe_allow_html=True)
    db_data = load_attendance()
    
    # upcoming session attendance 
    if not db_data.empty:
        latest_date = db_data.iloc[-1]['date'] 
        upcoming_data = db_data[db_data['date'] == latest_date]
        available_players = upcoming_data[upcoming_data['status'] == 'Available']['player'].tolist()
        
        st.markdown(f"### Upcoming Session: {latest_date}")
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
            st.download_button("Generate Attendance PDF", data=create_pdf(db_data), file_name="attendance.pdf", mime="application/pdf")
            pivot_df = db_data.pivot_table(index='player', columns='date', values='status', aggfunc='first').fillna("Unavailable")
            
            def color_matrix(val):
                if val == 'Available': return 'background-color: #bbf7d0; color: #166534'
                elif val == 'Unavailable': return 'background-color: #fecaca; color: #991b1b'
                return ''
            
            styled_df = pivot_df.style.map(color_matrix) if hasattr(pivot_df.style, 'map') else pivot_df.style.applymap(color_matrix)
            st.dataframe(styled_df, use_container_width=True)

    with tab2:
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
                    if add_player(new_name, new_pos):
                        st.success(f"Added {new_name} to the roster! Refresh to see them in the sidebar.")
                        st.rerun() # Automatically refresh the app to update the sidebar
                else:
                    st.error("Player name is required.")

elif nav == "My Stats":
    st.markdown(f"<h2>History: {current_user}</h2>", unsafe_allow_html=True)
    db_data = load_attendance()
    st.dataframe(db_data[db_data['player'] == current_user], use_container_width=True)