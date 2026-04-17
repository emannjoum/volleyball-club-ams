import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="JVC // Team Hub", page_icon="🏐", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .player-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    .stSegmentedControl { background: #f9fafb; padding: 10px; border-radius: 12px; }
    
    .brand-text {
        font-weight: 800;
        font-size: 2.2rem;
        letter-spacing: -2px;
        background: linear-gradient(90deg, #111827 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    div[data-testid="stMetricValue"] {
        font-weight: 800;
        color: #111827;
        letter-spacing: -1px;
    }
    </style>
""", unsafe_allow_html=True)

def get_skill_data():
    return pd.DataFrame(dict(
        r=[4, 3, 5, 4, 2],
        theta=['Hitting', 'Setting', 'Passing', 'Serving', 'Defense']
    ))

with st.sidebar:
    st.markdown("<h2 class='brand-text'>JVC</h2>", unsafe_allow_html=True)
    st.caption("VOLLEYBALL PERFORMANCE")
    st.divider()
    nav = st.radio("Menu", ["Dashboard", "My Stats", "Team Feed", "Admin"], label_visibility="collapsed")

if nav == "Dashboard":
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.markdown(f"<h1>Welcome back, player. <span style='color:#3b82f6'>Ready to work?</span></h1>", unsafe_allow_html=True)
        st.markdown("##### Next Session: Today @ 7:00 PM • Arena B")
    
    with col_h2:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.write("**12 Day Streak**")
            st.progress(0.8, text="3 sessions to next level")

    st.divider()

    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        st.markdown("### Check-in")
        status = st.segmented_control(
            "Your Status", ["Available", "Running Late", "Unavailable"],
            selection_mode="single", default="Available"
        )
        note = st.text_area("Note to Coach", placeholder="Add any details regarding your status.")
        if st.button("Confirm Attendance", use_container_width=True, type="primary"):
            st.toast("Status sent to Coach.")

    with c2:
        st.markdown("### Your Skill Profile")
        df_skill = get_skill_data()
        fig = px.line_polar(df_skill, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#3b82f6')
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    st.markdown("### Attendance Leaderboard")
    leaderboard_df = pd.DataFrame({
        "Player": ["heba T.", "player R.", "Lina M.", "Noor H.", "Sara K.", "Haya Z.", "Mayar A."],
        "Streak": [15, 12, 11, 8, 8, 7, 5],
        "Consistency": ["100%", "98%", "95%", "90%", "90%", "85%", "80%"]
    }).sort_values(by="Streak", ascending=False)

    st.dataframe(
        leaderboard_df,
        hide_index=True,
        use_container_width=True
    )

elif nav == "Admin":
    st.markdown("<h1 class='brand-text'>Command Center</h1>", unsafe_allow_html=True)

    with st.container(border=True):
        col_title, col_pdf = st.columns([2, 1])
        with col_title:
            st.markdown(f"### Today's Attendees ({datetime.now().strftime('%b %d')})")
            st.caption("Auto-filtered: Present & Late players only")
        
        with col_pdf:
            st.button("Download Master History (PDF)", use_container_width=True)

        todays_names = ["Lina M.", "heba T.", "player R.", "Haya Z.", "Noor H.", "Sara K.", "Mayar A."]
        st.code(", ".join(todays_names), language=None)
        st.caption("Copy names for squad list.")

    st.markdown("### Check-in Details")
    roster_status = pd.DataFrame({
        "Player": ["Lina M.", "heba T.", "player R.", "Haya Z.", "Noor H.", "Sara K.", "Mayar A.", "Noor D.", "Tala S."],
        "Status": ["In", "In", "Running Late", "In", "In", "Running Late", "In", "Out", "Out"],
        "Note": ["Ready!", "Coming from work", "Traffic", "", "Recovery", "5 mins late", "", "Academic", "Family"],
        "Arrival": ["3:45 PM", "3:50 PM", "4:15 PM", "3:55 PM", "3:58 PM", "4:10 PM", "3:40 PM", "-", "-"]
    })

    st.dataframe(
        roster_status,
        column_config={
            "Status": st.column_config.SelectboxColumn("Attendance", options=["In", "Out", "Running Late"]),
            "Player": st.column_config.TextColumn("Player Name", width="medium"),
            "Note": st.column_config.TextColumn("Notes", width="large"),
        },
        hide_index=True,
        use_container_width=True
    )

    st.divider()
    st.markdown("### Team Presence Pattern")
    dates = [f"Apr {i}" for i in range(10, 25)]
    players = [f"Player {i}" for i in range(1, 26)]
    data = np.random.choice([0, 1], size=(25, 15), p=[0.2, 0.8])
    fig_heat = px.imshow(data, x=dates, y=players, color_continuous_scale=[[0, '#f3f4f6'], [1, '#3b82f6']])
    fig_heat.update_coloraxes(showscale=False)
    fig_heat.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

elif nav == "My Stats":
    st.markdown("## Attendance History")
    history = pd.DataFrame({
        "Date": ["April 14", "April 12", "April 10", "April 07", "April 05"],
        "Status": ["Attended", "Attended", "Missed", "Attended", "Late"]
    })
    st.table(history)

elif nav == "Team Feed":
    st.markdown("<h1 class='brand-text'>Team Pulse</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### Coach's Bulletin")
        st.info("Practice Update: Focusing on 5-1 rotation drills today. Bring your knee pads. - Coach")
        st.caption("Posted 2 hours ago")

    st.divider()
    col_lead, col_achieve = st.columns([1, 1], gap="large")

    with col_lead:
        st.markdown("### Leaderboard")
        leader_data = pd.DataFrame({
            "Player": ["heba T.", "player R.", "Lina M.", "Noor H.", "Sara K."],
            "Streak": [15, 12, 8, 5, 4],
            "Rate": [100, 95, 92, 88, 85]
        })
        for _, row in leader_data.iterrows():
            c_name, c_rate = st.columns([2, 1])
            c_name.write(f"**{row['Player']}** ({row['Streak']})")
            c_rate.progress(row['Rate']/100)

    with col_achieve:
        st.markdown("### Activity Feed")
        activities = [
            {"player": "Lina M.", "action": "Reached Level 4", "tag": "SKILL UP"},
            {"player": "heba T.", "action": "30-Day Streak", "tag": "RELIABILITY"},
        ]
        for item in activities:
            with st.container(border=True):
                col_text, col_tag = st.columns([4, 1])
                with col_text:
                    st.markdown(f"**{item['player']}** — {item['action']}")
                with col_tag:
                    st.markdown(f"<span style='color: #3b82f6; font-size: 10px; font-weight: 800;'>{item['tag']}</span>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Weekly Team Synergy")
    m1, m2, m3 = st.columns(3)
    m1.metric("Avg. Attendance", "88%", "+2%")
    with m2:
        st.write("Team Energy")
        st.markdown("<div style='background-color: #f0fdf4; color: #166534; padding: 4px 12px; border-radius: 9999px; font-size: 14px; font-weight: 600; display: inline-block; border: 1px solid #bbf7d0;'>OPTIMAL</div>", unsafe_allow_html=True)
    m3.metric("Drill Completion", "94%", "5%")