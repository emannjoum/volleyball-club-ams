import streamlit as st
import pandas as pd
import numpy as np
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="JVC Check-in", page_icon="🏐", layout="centered")

if 'name' not in st.session_state:
    st.session_state.name = "Eman" 

user_name = st.session_state.name
st.markdown("""
    <style>
    .stMainBlockContainer {padding-top: 2rem;}
    [data-testid="stMetricValue"] {font-size: 1.8rem;}
    </style>
    """, unsafe_allow_html=True)

# will replace with supabase later
def get_mock_data():
    return pd.DataFrame({
        "Player": ["Lina", "Sara", "Mayar", "Haya", "Noor"],
        "Sessions": [12, 8, 15, 10, 5],
        "Status": ["Paid", "Paid", "Pending", "Paid", "Pending"]
    })

with st.sidebar:
    st.title("🏐 JVC Portal")
    st.info(f"Logged in as: {st.session_state.get('name', 'Guest')}")
    app_mode = st.radio("Menu", ["Player Check-in", "Coach Dashboard", "Fees"])
    st.divider()
    if st.button("Log Out", use_container_width=True):
        st.rerun()

if app_mode == "Player Check-in":

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.header(f"Hi, {user_name}!")
        st.markdown("🔥 **5 Practice Streak!** You're on fire.")
    with col_b:
        st.pills("Level", ["Varsity", "JV", "New"], default="Varsity", disabled=True)

    st.info("**Coach's Note:** yessir lets go idk.")

    # game history
    with st.expander("Your Game History", expanded=False):
        # mock history data  (in future this filters supabase by user_i)d
        history_data = pd.DataFrame({
            "Date": ["Mar 28", "Apr 1", "Apr 4"],
            "Opponent": ["Al-Ahli SC", "Orthodox Club", "Internal Scrimmage"],
            "Result": ["W (3-1)", "L (0-3)", "W (2-0)"],
            "Your Stats": ["12 Kills, 2 Aces", "5 Kills, 1 Block", "8 Kills, 4 Aces"]
        })
        st.table(history_data)

    # daily check-in
    st.write("### Today's Practice")
    with st.container(border=True):
        st.write("**Thursday, April 9th @ 4:00 PM**")
        status = st.segmented_control(
            "Set your status:",
            options=["In", "Late", "Out"],
            key="att_status"
        )
        if st.button("Confirm Attendance", type="primary", use_container_width=True):
            st.toast("Attendance Saved!", icon='🏐')

    st.divider()
    st.subheader("Team Leaderboard")
    
    t1, t2, t3 = st.columns(3)
    t1.metric("1st", "Sara", "950 pts")
    t2.metric("2nd", "Lina", "920 pts")
    t3.metric("3rd", "Mayar", "880 pts")
    
    with st.expander("Vertical Jump Leaderboard"): # or sth idk but the page feels too empty
        jump_df = pd.DataFrame({
            "Player": ["Lina", "Sara", "Noor"],
            "Max Reach": ["250 cm", "242 cm", "238 cm"]
        })
        st.dataframe(jump_df, use_container_width=True, hide_index=True)

    st.subheader("Attendance Chart")

    trend_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr"],
        "Attendance %": [70, 85, 82, 95],
        "Target": [90, 90, 90, 90]
    })

    st.line_chart(trend_data, x="Month", y=["Attendance %", "Target"], color=["#C48FDC", "#46B290"])
    st.caption("Purple: Your Attendance | Green: Team Target")

elif app_mode == "Coach Dashboard":
    st.header("Coach's Overview")
    df = get_mock_data()
    
    c1, c2 = st.columns(2)
    c1.metric("Expected Today", "14 Players")
    c2.metric("Attendance Rate", "88%")
    
    st.write("### Attendance Distribution")
    st.bar_chart(df, x="Player", y="Sessions", color="#46B290")
    
    st.write("### Full Roster")
    st.dataframe(df, use_container_width=True)

elif app_mode == "Fees":
    st.header("Team Fund")
    df = get_mock_data()
    
    with st.container(border=True):
        st.write("Your April Fees: **Paid**")
    
    st.write("### Monthly Collection")
    st.table(df[["Player", "Status"]])

st.caption("v1.0-alpha")