import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database as db
from utils import get_next_session_date, get_upcoming_sessions_list, calculate_streaks, create_pdf

def _stat_card(label, value, accent_color="#6366F1", sub=None):
    sub_html = f"<span class='card-sub'>{sub}</span>" if sub else ""
    return f"""
    <div class='stat-card'>
        <div class='card-accent' style='background:{accent_color};'></div>
        <p class='card-label'>{label}</p>
        <h2 class='card-value' style='color:{accent_color};'>{value}</h2>
        {sub_html}
    </div>"""

def _section_header(title, eyebrow=None):
    eyebrow_html = f"<span class='section-eyebrow'>{eyebrow}</span>" if eyebrow else ""
    return f"""<div class='section-header'>{eyebrow_html}<h3 class='section-title'>{title}</h3></div>"""

def render_player_dashboard(current_user, radar_label_color):
    first_name = current_user.split()[0]
    st.markdown(f"""
        <div class='page-hero'>
            <span class='hero-eyebrow'>TEAM HUB</span>
            <h1 class='hero-title'>Welcome back, <span class='hero-accent'>{first_name}</span></h1>
        </div>
    """, unsafe_allow_html=True)

    overrides  = db.get_schedule_overrides()
    next_session = get_next_session_date(overrides)
    db_data    = db.load_attendance()
    stats      = db.load_player_stats(current_user)

    skill_names  = ['Hitting', 'Setting', 'Passing', 'Serving', 'Defense']
    skill_values = [stats['hitting'], stats['setting'], stats['passing'],
                    stats['serving'], stats['defense']]
    top_skill    = skill_names[skill_values.index(max(skill_values))]
    current_credits = db.load_player_credits(current_user)

    # ── Metric Row ──────────────────────────────
    col1, col2, col3 = st.columns(3)
    credit_color = "#10B981" if current_credits > 0 else "#EF4444"
    with col1:
        st.markdown(_stat_card("NEXT PRACTICE", next_session, "#6366F1"), unsafe_allow_html=True)
    with col2:
        st.markdown(_stat_card("SESSIONS LEFT", f"{current_credits}", credit_color), unsafe_allow_html=True)
    with col3:
        st.markdown(_stat_card("TOP SKILL", top_skill, "#F59E0B"), unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Main Content ────────────────────────────
    c1, c2 = st.columns([1, 1.5], gap="large")

    with c1:
        st.markdown(f"""
            <div class='panel'>
                {_section_header("Check-in", f"FOR {next_session.upper()}")}
            </div>
        """, unsafe_allow_html=True)

        current_status = db.get_current_attendance_status(current_user, next_session)
        if current_status == "In":
            st.markdown("<div class='status-badge status-in'><span class='pulse-dot'></span> Status — In</div>", unsafe_allow_html=True)
        elif current_status == "Double Session":
            st.markdown("<div class='status-badge status-in' style='color:#4ADE80;'><span class='pulse-dot' style='background:#4ADE80;'></span> Status — Double Session</div>", unsafe_allow_html=True)
        elif current_status:
            st.markdown("<div class='status-badge status-out'>Marked Out</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='helper-text'>Let the coach know if you'll be on the court.</p>", unsafe_allow_html=True)

        status = st.segmented_control(
            "Your Status",
            ["In", "Double Session", "Out"],
            default=current_status if current_status else "In",
            key="player_status_ctrl"
        )
        cost_map = {"In": 1, "Double Session": 2, "Out": 0}
        selected_cost = cost_map.get(status, 0)
        
        if st.button("Save Status", use_container_width=True):
            # Check balance before saving
            if current_credits - selected_cost < 0:
                st.warning(f"You don't have enough credits for a {status}. You will go into debt.")
            
            if db.save_attendance(current_user, status, next_session):
                st.success(f"Status saved as {status} for {next_session}")
                st.rerun()

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # Streaks
        st.markdown(_section_header("Attendance Streaks", "TEAM"), unsafe_allow_html=True)
        if not db_data.empty:
            streak_df = calculate_streaks(db_data)
            max_val   = int(streak_df['Max Streak'].max()) if not streak_df.empty else 10
            if max_val == 0: max_val = 1

            html_str = "<div class='streak-list'>"
            for rank, (_, row) in enumerate(streak_df.head(5).iterrows(), start=1):
                player = row['Player']
                streak = row['Max Streak']
                pct    = streak / max_val * 100
                medal  = ["🥇","🥈","🥉","",""][rank - 1]
                html_str += f"""
                <div class='streak-row'>
                    <div class='streak-rank'>{medal if medal else rank}</div>
                    <div class='streak-info'>
                        <span class='streak-name'>{player}</span>
                        <div class='streak-bar-wrap'>
                            <div class='streak-bar' style='width:{pct}%'></div>
                        </div>
                    </div>
                    <div class='streak-count'>{streak}</div>
                </div>"""
            html_str += "</div>"
            st.markdown(html_str, unsafe_allow_html=True)
        else:
            st.markdown("<p class='helper-text'>No attendance data yet.</p>", unsafe_allow_html=True)

    with c2:
        st.markdown(_section_header("Skill Radar", "YOUR PERFORMANCE"), unsafe_allow_html=True)
        df_skill = pd.DataFrame(dict(r=skill_values, theta=skill_names))
        fig = px.line_polar(df_skill, r='r', theta='theta', line_close=True)
        fig.update_traces(
            fill='toself',
            line_color='#6366F1',
            fillcolor='rgba(99, 102, 241, 0.18)'
        )
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(
                    visible=True, range=[0, 5],
                    tickfont=dict(size=9, color='#64748B'),
                    gridcolor='rgba(99,102,241,0.15)',
                    linecolor='rgba(99,102,241,0.2)'
                ),
                angularaxis=dict(
                    visible=True, showticklabels=True,
                    tickfont=dict(size=13, color=radar_label_color, family='Space Grotesk, sans-serif'),
                    gridcolor='rgba(99,102,241,0.12)',
                    linecolor='rgba(99,102,241,0.2)'
                )
            ),
            showlegend=False,
            height=400,
            margin=dict(l=80, r=80, t=40, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Skill breakdown bars
        html_skills = "<div class='skill-breakdown'>"
        for name, val in zip(skill_names, skill_values):
            pct = val / 5 * 100
            html_skills += f"""
            <div class='skill-row'>
                <span class='skill-label'>{name}</span>
                <div class='skill-bar-wrap'>
                    <div class='skill-bar-fill' style='width:{pct}%'></div>
                </div>
                <span class='skill-num'>{val}/5</span>
            </div>"""
        html_skills += "</div>"
        st.markdown(html_skills, unsafe_allow_html=True)

def render_player_stats(current_user, grid_empty):
    st.markdown(f"""
        <div class='page-hero'>
            <span class='hero-eyebrow'>HISTORY</span>
            <h1 class='hero-title'>Season<span class='hero-accent'> Chronicle</span></h1>
        </div>
    """, unsafe_allow_html=True)

    db_data = db.load_attendance()

    if not db_data.empty:
        user_data = db_data[db_data['player'] == current_user].copy()
        user_data['Month'] = user_data['date'].apply(lambda x: x.split(' ')[0])
        unique_months = list(dict.fromkeys(user_data['Month']))
        unique_months.reverse()
        in_months = ["All Time"] + unique_months
        default_idx = 1 if len(in_months) > 1 else 0

        filter_col, _ = st.columns([1, 2])
        with filter_col:
            selected_month = st.selectbox("Filter by Month", in_months, index=default_idx)

        if selected_month != "All Time":
            user_data = user_data[user_data['Month'] == selected_month]

        total_sessions  = len(user_data)
        attended        = len(user_data[user_data['status'] == 'In'])
        attendance_rate = int(attended / total_sessions * 100) if total_sessions > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(_stat_card("CHECK-INS LOGGED", total_sessions, "#6366F1"), unsafe_allow_html=True)
        with col2:
            st.markdown(_stat_card("PRACTICES ATTENDED", attended, "#10B981"), unsafe_allow_html=True)
        with col3:
            rate_color = "#10B981" if attendance_rate >= 75 else "#F59E0B" if attendance_rate >= 50 else "#EF4444"
            st.markdown(_stat_card("ATTENDANCE RATE", f"{attendance_rate}%", rate_color), unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        selected_cols = ['date', 'status']
        def highlight_attendance(val):
            if val == 'In':      return 'color: #10B981; font-weight: 600'
            if val == 'Double Session': return 'color: #6366F1; font-weight: 600'
            if val == 'Out':    return 'color: #EF4444'
            return ''

        st.markdown(_section_header("Session Log"), unsafe_allow_html=True)
        st.dataframe(
            user_data[selected_cols].style.map(highlight_attendance, subset=['status'])
            if hasattr(user_data[selected_cols].style, 'map')
            else user_data[selected_cols].style.applymap(highlight_attendance, subset=['status']),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(_section_header("Activity Grid", "ALL SESSIONS"), unsafe_allow_html=True)
        sorted_data = user_data.sort_values('created_at') if 'created_at' in user_data.columns else user_data
        squares_html = "<div class='activity-grid'>"
        for _, row in sorted_data.iterrows():
            if row['status'] == 'In':
                color, glow = "#6366F1", "0 0 6px rgba(99,102,241,0.6)"
            elif row['status'] == 'Double Session':
                color, glow = "#10B981", "0 0 6px rgba(16,185,129,0.6)"
            else:
                color, glow = grid_empty, "none"
            squares_html += f"<div class='activity-square' title='{row['date']} — {row['status']}' style='background:{color}; box-shadow:{glow};'></div>"
        squares_html += "</div>"
        st.markdown(squares_html, unsafe_allow_html=True)
    else:
        st.info("No attendance data recorded yet.")

def render_admin():
    st.markdown("""
        <div class='page-hero'>
            <span class='hero-eyebrow'>COACH VIEW</span>
            <h1 class='hero-title'>Admin <span class='hero-accent'>Control</span></h1>
        </div>
    """, unsafe_allow_html=True)

    overrides      = db.get_schedule_overrides()
    upcoming_date  = get_next_session_date(overrides)
    db_data        = db.load_attendance()
    players_list   = db.load_players()

    with st.expander(f"Floor Override — {upcoming_date}", expanded=False):
        st.markdown("<p class='helper-text'>Manually flip a player's attendance. Session fees adjust automatically.</p>", unsafe_allow_html=True)
        if players_list:
            override_cols = st.columns(4)
            for i, p in enumerate(players_list):
                col = override_cols[i % 4]
                curr_stat = db.get_current_attendance_status(p, upcoming_date)
                is_avail  = (curr_stat == "In")
                changed   = col.toggle(f"{p}", value=is_avail, key=f"quick_tgl_{p}")
                if changed != is_avail:
                    new_stat = "In" if changed else "Out"
                    if db.save_attendance(p, new_stat, upcoming_date):
                        st.rerun()

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if not db_data.empty:
        upcoming_data     = db_data[db_data['date'] == upcoming_date]
        in_players = upcoming_data[upcoming_data['status'] == 'In']['player'].tolist()

        st.markdown(_section_header(f"Session Summary — {upcoming_date}", "NEXT UP"), unsafe_allow_html=True)

        col_count, col_names = st.columns([1, 4])
        with col_count:
            st.markdown(_stat_card("ATTENDING", len(in_players), "#6366F1"), unsafe_allow_html=True)
        with col_names:
            if in_players:
                pills_html = "<div class='player-pill-row'>" + "".join(
                    f"<span class='player-pill'>{p}</span>" for p in in_players
                ) + "</div>"
                st.markdown(pills_html, unsafe_allow_html=True)
            else:
                st.markdown("<p class='helper-text'>No players confirmed yet.</p>", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Attendance Data", "Player Stats", "Manage Roster"])

    with tab1:
        if not db_data.empty:
            db_data['Month'] = db_data['date'].apply(lambda x: x.split(' ')[0])
            unique_months    = list(dict.fromkeys(db_data['Month']))
            unique_months.reverse()
            in_months = ["All Time"] + unique_months
            default_idx      = 1 if len(in_months) > 1 else 0

            matrix_col, _ = st.columns([1, 2])
            with matrix_col:
                selected_matrix_month = st.selectbox("Filter Matrix by Month", in_months, index=default_idx)

            filtered_db = db_data if selected_matrix_month == "All Time" else db_data[db_data['Month'] == selected_matrix_month]

            if not filtered_db.empty:
                pivot_df = (filtered_db
                    .pivot_table(index='player', columns='date', values='status', aggfunc='first')
                    .fillna("Out")
                    .reset_index())

                st.download_button(
                    "⬇ Download Attendance PDF",
                    data=create_pdf(pivot_df, f"JVC Attendance Report — {selected_matrix_month}"),
                    file_name="attendance_report.pdf",
                    mime="application/pdf"
                )

                def color_matrix(val):
                    if val == 'In':      return 'background-color:#1e3a5f; color:#60A5FA; font-weight:600'
                    elif val == 'Double Session': return 'background-color:#14532d; color:#4ADE80; font-weight:700'
                    elif val == 'Out':  return 'background-color:#3b1f1f; color:#F87171'
                    return ''

                display_df = pivot_df.set_index('player')
                styled_df  = display_df.style.map(color_matrix) if hasattr(display_df.style, 'map') else display_df.style.applymap(color_matrix)
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.info("No records for this month.")

    with tab2:
        if players_list:
            target  = st.selectbox("Select Player", players_list)
            cur_avg = db.load_player_stats(target)
            st.markdown(f"""
                <div class='info-bar'>
                    Current averages —
                    <b>Hitting</b> {cur_avg['hitting']} ·
                    <b>Setting</b> {cur_avg['setting']} ·
                    <b>Passing</b> {cur_avg['passing']} ·
                    <b>Serving</b> {cur_avg['serving']} ·
                    <b>Defense</b> {cur_avg['defense']}
                </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                h  = st.slider("Hitting",  1, 5, 3)
                s  = st.slider("Setting",  1, 5, 3)
                p  = st.slider("Passing",  1, 5, 3)
            with col2:
                sv = st.slider("Serving",  1, 5, 3)
                d  = st.slider("Defense",  1, 5, 3)

            if st.button("Log Evaluation", use_container_width=True):
                if db.save_stats(target, h, s, p, sv, d):
                    st.success("Evaluation logged. Radar average updated.")
        else:
            st.info("Add players in the Manage Roster tab first.")

    with tab3:
        rost_col1, rost_col2 = st.columns(2, gap="large")
        with rost_col1:
            st.subheader("Add New Player")
            with st.form("new_player_form"):
                new_name = st.text_input("Full Name / Display Name")
                new_pos  = st.selectbox("Position", [
                    "None","Outside Hitter","Middle Blocker",
                    "Setter","Libero","Opposite","Defensive Specialist"
                ])
                if st.form_submit_button("Create Profile"):
                    if new_name:
                        pin = db.add_player(new_name, new_pos)
                        if pin:
                            st.success(f"Added {new_name}. Login PIN: **{pin}**")
                            st.rerun()
                    else:
                        st.error("Player name is required.")

        with rost_col2:
            st.subheader("Edit Existing Player")
            if players_list:
                edit_target = st.selectbox("Select Player to Edit", players_list)
                if edit_target:
                    try:
                        p_data = db.conn.table("players").select("*").eq("name", edit_target).execute().data[0]
                    except:
                        p_data = {"name": edit_target, "position": "None", "access_code": "0000"}

                    with st.form("edit_player_form"):
                        e_name   = st.text_input("Name",     value=p_data['name'])
                        pos_list = ["None","Outside Hitter","Middle Blocker",
                                    "Setter","Libero","Opposite","Defensive Specialist"]
                        default_ix = pos_list.index(p_data['position']) if p_data['position'] in pos_list else 0
                        e_pos    = st.selectbox("Position", pos_list, index=default_ix)
                        e_pin    = st.text_input("PIN Code", value=p_data['access_code'])
                        if st.form_submit_button("Save Changes"):
                            if db.edit_player(edit_target, e_name, e_pos, e_pin):
                                st.success("Player details updated.")
                                st.rerun()

        st.divider()
        st.subheader("Current Roster & PINs")
        roster_df = db.get_roster_with_pins()
        if not roster_df.empty:
            roster_df = roster_df.rename(columns={"name":"Player","position":"Position","access_code":"Login PIN"})
            st.dataframe(roster_df, use_container_width=True, hide_index=True)

def render_finances(show_history_report):
    st.markdown("""
        <div class='page-hero'>
            <span class='hero-eyebrow'>OPERATIONS</span>
            <h1 class='hero-title'>Financial <span class='hero-accent'>HQ</span></h1>
        </div>
    """, unsafe_allow_html=True)

    current_month  = datetime.now().strftime('%b %Y')
    hist_df        = db.load_payment_history()
    players_list   = db.load_players()

    month_sessions = 0
    if not hist_df.empty:
        hist_df['is_current_month'] = hist_df['Date'].str.contains(datetime.now().strftime('%b'))
        month_sessions = hist_df[hist_df['is_current_month']]['Sessions Added'].sum()

    st.markdown(_stat_card(f"SESSIONS PURCHASED — {current_month}", month_sessions, "#F59E0B"), unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.markdown(_section_header("Record Payment"), unsafe_allow_html=True)
        if players_list:
            with st.form("payment_form"):
                target_player = st.selectbox("Select Player", players_list)
                plan_type     = st.radio("Plan", ["Monthly (8 Sessions)", "Daily (1 Session)", "Custom Number"])
                custom_amount = st.number_input("Custom sessions", min_value=-50, max_value=50, value=0)
                if st.form_submit_button("Confirm Payment", use_container_width=True):
                    sessions_to_add = 8 if plan_type == "Monthly (8 Sessions)" else (1 if plan_type == "Daily (1 Session)" else custom_amount)
                    if db.update_player_credits(target_player, sessions_to_add, plan_type):
                        st.success(f"{sessions_to_add} session(s) added for {target_player}.")
                        st.rerun()
        else:
            st.info("No players in.")

    with col2:
        overrides     = db.get_schedule_overrides()
        upcoming_date = get_next_session_date(overrides)
        st.markdown(_section_header(f"Payments — {upcoming_date}", "TODAY"), unsafe_allow_html=True)

        try:
            att_query  = db.conn.table("attendance").select("player").eq("date", upcoming_date).eq("status", "In").execute()
            if att_query.data:
                attendees  = [row['player'] for row in att_query.data]
                cred_query = db.conn.table("player_credits").select("player, remaining_sessions").execute()
                df_creds   = pd.DataFrame(cred_query.data)
                df_today   = df_creds[df_creds['player'].isin(attendees)].copy()
                df_today['Payment Status'] = df_today['remaining_sessions'].apply(lambda x: "Paid" if x >= 0 else "Owes")
                df_today   = df_today[['player','Payment Status']].rename(columns={"player":"Player"})

                def highlight_status(val):
                    if 'Paid' in str(val): return 'color: #10B981; font-weight: 600'
                    if 'Owes' in str(val): return 'color: #EF4444; font-weight: 700'
                    return ''

                st.dataframe(
                    df_today.style.map(highlight_status, subset=['Payment Status'])
                    if hasattr(df_today.style, 'map')
                    else df_today.style.applymap(highlight_status, subset=['Payment Status']),
                    use_container_width=True, hide_index=True
                )
            else:
                st.markdown("<p class='helper-text'>No check-ins yet for this session.</p>", unsafe_allow_html=True)
        except Exception:
            st.error("Could not load payment data.")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(_section_header("Reports & Export", "TOOLS"), unsafe_allow_html=True)

    if show_history_report:
        rep_col1, rep_col2 = st.columns(2, gap="large")
    else:
        rep_col1, rep_col2 = st.columns([1, 1])

    with rep_col1:
        st.markdown("#### Debt Report")
        query = db.conn.table("player_credits").select("player, remaining_sessions").lt("remaining_sessions", 0).order("remaining_sessions").execute()
        if query.data:
            df_debt = pd.DataFrame(query.data)
            df_debt = df_debt.rename(columns={"player":"Player","remaining_sessions":"Sessions Owed"})
            df_debt["Sessions Owed"] = df_debt["Sessions Owed"].abs()
            st.dataframe(df_debt, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇ Download Debt Report (PDF)",
                data=create_pdf(df_debt, "JVC — Players In Debt"),
                file_name=f"JVC_Debt_Report_{datetime.now().strftime('%b_%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.success("Everyone is paid up!")

    if show_history_report:
        with rep_col2:
            st.markdown("#### Payment History")
            if not hist_df.empty:
                st.dataframe(hist_df, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇ Download History (PDF)",
                    data=create_pdf(hist_df, "JVC — Payment Transaction Log"),
                    file_name=f"JVC_Payment_History_{datetime.now().strftime('%b_%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("No transactions recorded yet.")


#  SESSION MANAGER
def render_session_manager():
    st.markdown("""
        <div class='page-hero'>
            <span class='hero-eyebrow'>SCHEDULE</span>
            <h1 class='hero-title'>Session <span class='hero-accent'>Manager</span></h1>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<p class='helper-text' style='margin-bottom:1.5rem'>Control the team schedule. Auto-generated Sun/Thu practices appear here. Cancel or add custom dates.</p>", unsafe_allow_html=True)

    overrides      = db.get_schedule_overrides()
    upcoming_list  = get_upcoming_sessions_list(overrides)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(_section_header("Upcoming Schedule", "NEXT 7 SESSIONS"), unsafe_allow_html=True)
        if upcoming_list:
            for d in upcoming_list[:7]:
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"<div class='session-chip'>{d}</div>", unsafe_allow_html=True)
                if c2.button("Cancel", key=f"cancel_{d}"):
                    if db.add_schedule_override(d, "Cancelled"):
                        st.rerun()
        else:
            st.info("No upcoming sessions found.")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(_section_header("Add Custom Session"), unsafe_allow_html=True)
        st.markdown("<p class='helper-text'>Need a Tuesday practice? Add it here.</p>", unsafe_allow_html=True)
        custom_date = st.date_input("Select Date")
        if st.button("Add Session", use_container_width=True):
            date_str = custom_date.strftime("%b %d")
            if db.add_schedule_override(date_str, "Added"):
                st.success(f"Added {date_str} to the schedule.")
                st.rerun()

    with col2:
        st.markdown(_section_header("Cancelled Sessions", "REMOVED"), unsafe_allow_html=True)
        cancelled_list = [x['session_date'] for x in overrides if x['status'] == 'Cancelled']
        if cancelled_list:
            for c in cancelled_list:
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"<div class='session-chip cancelled-chip'>{c}</div>", unsafe_allow_html=True)
                if c2.button("Restore", key=f"restore_{c}"):
                    if db.delete_schedule_override(c):
                        st.rerun()
        else:
            st.markdown("<p class='helper-text'>No sessions currently cancelled.</p>", unsafe_allow_html=True)