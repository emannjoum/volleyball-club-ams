import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database as db
from utils import get_next_session_date, get_upcoming_sessions_list, calculate_streaks, create_pdf

def _stat_card(label, value, accent_color="#7C8EF5", sub=None):
    sub_html = f"<span class='card-sub'>{sub}</span>" if sub else ""
    return f"""
    <div class='stat-card' style='--card-accent:{accent_color};'>
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
            <span class='hero-eyebrow'>Team Hub</span>
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
    credit_color = "#5CB88A" if current_credits > 0 else "#E06B6B"
    with col1:
        st.markdown(_stat_card("Next practice", next_session, "#7C8EF5"), unsafe_allow_html=True)
    with col2:
        st.markdown(_stat_card("Sessions left", f"{current_credits}", credit_color), unsafe_allow_html=True)
    with col3:
        st.markdown(_stat_card("Top skill", top_skill, "#D4A574"), unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Main Content ────────────────────────────
    c1, c2 = st.columns([1, 1.5], gap="large")

    with c1:
        with st.container(border=True):
            st.markdown(_section_header("Check-in", next_session), unsafe_allow_html=True)

            current_status = db.get_current_attendance_status(current_user, next_session)
            if current_status == "In":
                st.markdown("<div class='status-badge status-in'><span class='status-dot'></span> You're in</div>", unsafe_allow_html=True)
            elif current_status == "Double Session":
                st.markdown("<div class='status-badge status-in'><span class='status-dot'></span> Double session</div>", unsafe_allow_html=True)
            elif current_status:
                st.markdown("<div class='status-badge status-out'><span class='status-dot'></span> Marked out</div>", unsafe_allow_html=True)
            else:
                st.markdown("<p class='helper-text'>Let the coach know if you'll be on the court.</p>", unsafe_allow_html=True)

            status = st.segmented_control(
                "Your status",
                ["In", "Double Session", "Out"],
                default=current_status if current_status else "In",
                key="player_status_ctrl"
            )
            cost_map = {"In": 1, "Double Session": 2, "Out": 0}
            selected_cost = cost_map.get(status, 0)

            if st.button("Save status", use_container_width=True):
                if current_credits - selected_cost < 0:
                    st.warning(f"You don't have enough credits for a {status}. You will go into debt.")

                if db.save_attendance(current_user, status, next_session):
                    st.success(f"Status saved as {status} for {next_session}")
                    st.rerun()

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(_section_header("Attendance streaks", "Team"), unsafe_allow_html=True)
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
        with st.container(border=True):
            st.markdown(_section_header("Skill radar", "Your performance"), unsafe_allow_html=True)
            df_skill = pd.DataFrame(dict(r=skill_values, theta=skill_names))
            fig = px.line_polar(df_skill, r='r', theta='theta', line_close=True)
            fig.update_traces(
                fill='toself',
                line_color='#7C8EF5',
                fillcolor='rgba(124, 142, 245, 0.14)',
                line_width=2,
            )
            fig.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(
                        visible=True, range=[0, 5],
                        tickfont=dict(size=9, color='#8B95A8'),
                        gridcolor='rgba(255,255,255,0.06)',
                        linecolor='rgba(255,255,255,0.08)'
                    ),
                    angularaxis=dict(
                        visible=True, showticklabels=True,
                        tickfont=dict(size=12, color=radar_label_color, family='Outfit, sans-serif'),
                        gridcolor='rgba(255,255,255,0.05)',
                        linecolor='rgba(255,255,255,0.08)'
                    )
                ),
                showlegend=False,
                height=400,
                margin=dict(l=80, r=80, t=40, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

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
    st.markdown("""
        <div class='page-hero'>
            <span class='hero-eyebrow'>History</span>
            <h1 class='hero-title'>Season <span class='hero-accent'>chronicle</span></h1>
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
            selected_month = st.selectbox("Filter by month", in_months, index=default_idx)

        if selected_month != "All Time":
            user_data = user_data[user_data['Month'] == selected_month]

        total_sessions  = len(user_data)
        attended        = len(user_data[user_data['status'] == 'In'])
        attendance_rate = int(attended / total_sessions * 100) if total_sessions > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(_stat_card("Check-ins logged", total_sessions, "#7C8EF5"), unsafe_allow_html=True)
        with col2:
            st.markdown(_stat_card("Practices attended", attended, "#5CB88A"), unsafe_allow_html=True)
        with col3:
            rate_color = "#5CB88A" if attendance_rate >= 75 else "#D4A574" if attendance_rate >= 50 else "#E06B6B"
            st.markdown(_stat_card("Attendance rate", f"{attendance_rate}%", rate_color), unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        selected_cols = ['date', 'status']
        def highlight_attendance(val):
            if val == 'In':      return 'color: #5CB88A; font-weight: 600'
            if val == 'Double Session': return 'color: #7C8EF5; font-weight: 600'
            if val == 'Out':    return 'color: #E06B6B'
            return ''

        st.markdown(_section_header("Session log"), unsafe_allow_html=True)
        st.dataframe(
            user_data[selected_cols].style.map(highlight_attendance, subset=['status'])
            if hasattr(user_data[selected_cols].style, 'map')
            else user_data[selected_cols].style.applymap(highlight_attendance, subset=['status']),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(_section_header("Activity grid", "All sessions"), unsafe_allow_html=True)
        sorted_data = user_data.sort_values('created_at') if 'created_at' in user_data.columns else user_data
        squares_html = "<div class='activity-grid'>"
        for _, row in sorted_data.iterrows():
            if row['status'] == 'In':
                color = "#7C8EF5"
            elif row['status'] == 'Double Session':
                color = "#5CB88A"
            else:
                color = grid_empty
            squares_html += f"<div class='activity-square' title='{row['date']} — {row['status']}' style='background:{color};'></div>"
        squares_html += "</div>"
        st.markdown(squares_html, unsafe_allow_html=True)
    else:
        st.info("No attendance data recorded yet.")

def render_admin():
    st.markdown("""
        <div class='page-hero'>
            <span class='hero-eyebrow'>Coach view</span>
            <h1 class='hero-title'>Admin <span class='hero-accent'>control</span></h1>
        </div>
    """, unsafe_allow_html=True)

    overrides      = db.get_schedule_overrides()
    upcoming_date  = get_next_session_date(overrides)
    db_data        = db.load_attendance()
    players_list   = db.load_players()

    with st.expander(f"Floor override — {upcoming_date}", expanded=False):
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

        st.markdown(_section_header(f"Session summary — {upcoming_date}", "Next up"), unsafe_allow_html=True)

        col_count, col_names = st.columns([1, 4])
        with col_count:
            st.markdown(_stat_card("Attending", len(in_players), "#7C8EF5"), unsafe_allow_html=True)
        with col_names:
            if in_players:
                # the players' pills
                pills_html = "<div class='player-pill-row'>" + "".join(
                    f"<span class='player-pill'>{p}</span>" for p in in_players
                ) + "</div>"
                st.markdown(pills_html, unsafe_allow_html=True)
                
                whatsapp_header = f"🏐 Practice — {upcoming_date}\n" # for WhatsApp msg of coach 

                whatsapp_names = "\n".join([f"{i+1}. {p}" for i, p in enumerate(in_players)])
                full_roster_text = whatsapp_header + whatsapp_names
                
                st.markdown("<p style='font-size:0.78rem; color:#8B95A8; margin-top:0.75rem; margin-bottom:0.25rem;'>Copy list for WhatsApp</p>", unsafe_allow_html=True)
                st.code(full_roster_text, language=None) # copy button
            else:
                st.markdown("<p class='helper-text'>No players confirmed yet.</p>", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Attendance", "Player stats", "Roster"])

    with tab1:
        if not db_data.empty:
            db_data['Month'] = db_data['date'].apply(lambda x: x.split(' ')[0])
            unique_months    = list(dict.fromkeys(db_data['Month']))
            unique_months.reverse()
            in_months = ["All Time"] + unique_months
            default_idx      = 1 if len(in_months) > 1 else 0

            matrix_col, _ = st.columns([1, 2])
            with matrix_col:
                selected_matrix_month = st.selectbox("Filter by month", in_months, index=default_idx)

            filtered_db = db_data if selected_matrix_month == "All Time" else db_data[db_data['Month'] == selected_matrix_month]

            if not filtered_db.empty:
                pivot_df = (filtered_db
                    .pivot_table(index='player', columns='date', values='status', aggfunc='first')
                    .fillna("Out")
                    .reset_index())

                st.download_button(
                    "Download attendance PDF",
                    data=create_pdf(pivot_df, f"JVC Attendance Report — {selected_matrix_month}"),
                    file_name="attendance_report.pdf",
                    mime="application/pdf"
                )

                def color_matrix(val):
                    if val == 'In':      return 'background-color:rgba(124,142,245,0.12); color:#7C8EF5; font-weight:500'
                    elif val == 'Double Session': return 'background-color:rgba(92,184,138,0.12); color:#5CB88A; font-weight:600'
                    elif val == 'Out':  return 'background-color:rgba(224,107,107,0.08); color:#E06B6B'
                    return ''

                display_df = pivot_df.set_index('player')
                styled_df  = display_df.style.map(color_matrix) if hasattr(display_df.style, 'map') else display_df.style.applymap(color_matrix)
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.info("No records for this month.")

    with tab2:
        if players_list:
            target  = st.selectbox("Select player", players_list)
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

            if st.button("Log evaluation", use_container_width=True):
                if db.save_stats(target, h, s, p, sv, d):
                    st.success("Evaluation logged. Radar average updated.")
        else:
            st.info("Add players in the Manage Roster tab first.")

    with tab3:
        rost_col1, rost_col2 = st.columns(2, gap="large")
        with rost_col1:
            st.subheader("Add player")
            with st.form("new_player_form"):
                new_name = st.text_input("Full name")
                new_pos  = st.selectbox("Position", [
                    "None","Outside Hitter","Middle Blocker",
                    "Setter","Libero","Opposite","Defensive Specialist"
                ])
                if st.form_submit_button("Create profile"):
                    if new_name:
                        pin = db.add_player(new_name, new_pos)
                        if pin:
                            st.success(f"Added {new_name}. Login PIN: **{pin}**")
                            st.rerun()
                    else:
                        st.error("Player name is required.")

        with rost_col2:
            st.subheader("Edit player")
            if players_list:
                edit_target = st.selectbox("Select player to edit", players_list)
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
                        e_pin    = st.text_input("PIN code", value=p_data['access_code'])
                        if st.form_submit_button("Save changes"):
                            if db.edit_player(edit_target, e_name, e_pos, e_pin):
                                st.success("Player details updated.")
                                st.rerun()

        st.divider()
        st.subheader("Current roster")
        roster_df = db.get_roster_with_pins()
        if not roster_df.empty:
            roster_df = roster_df.rename(columns={"name":"Player","position":"Position","access_code":"Login PIN"})
            st.dataframe(roster_df, use_container_width=True, hide_index=True)

def render_finances(show_history_report):
    st.markdown("""
        <div class='page-hero'>
            <span class='hero-eyebrow'>Operations</span>
            <h1 class='hero-title'>Financial <span class='hero-accent'>overview</span></h1>
        </div>
    """, unsafe_allow_html=True)

    current_month  = datetime.now().strftime('%b %Y')
    hist_df        = db.load_payment_history()
    players_list   = db.load_players()

    month_sessions = 0
    if not hist_df.empty:
        hist_df['is_current_month'] = hist_df['Date'].str.contains(datetime.now().strftime('%b'))
        month_sessions = hist_df[hist_df['is_current_month']]['Sessions Added'].sum()

    st.markdown(_stat_card(f"Sessions purchased · {current_month}", month_sessions, "#D4A574"), unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown(_section_header("Record payment"), unsafe_allow_html=True)
            if players_list:
                with st.form("payment_form"):
                    target_player = st.selectbox("Select player", players_list)
                    plan_type     = st.radio("Plan", ["Monthly (8 sessions)", "Daily (1 session)", "Custom"])
                    custom_amount = st.number_input("Custom sessions", min_value=-50, max_value=50, value=0)
                    if st.form_submit_button("Confirm payment", use_container_width=True):
                        sessions_to_add = 8 if plan_type == "Monthly (8 sessions)" else (1 if plan_type == "Daily (1 session)" else custom_amount)
                        if db.update_player_credits(target_player, sessions_to_add, plan_type):
                            st.success(f"{sessions_to_add} session(s) added for {target_player}.")
                            st.rerun()
            else:
                st.info("No players in.")

    with col2:
        overrides     = db.get_schedule_overrides()
        upcoming_date = get_next_session_date(overrides)
        with st.container(border=True):
            st.markdown(_section_header(f"Payments · {upcoming_date}", "Today"), unsafe_allow_html=True)

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
                        if 'Paid' in str(val): return 'color: #5CB88A; font-weight: 600'
                        if 'Owes' in str(val): return 'color: #E06B6B; font-weight: 600'
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
    st.markdown(_section_header("Reports & export", "Tools"), unsafe_allow_html=True)

    if show_history_report:
        rep_col1, rep_col2 = st.columns(2, gap="large")
    else:
        rep_col1, rep_col2 = st.columns([1, 1])

    with rep_col1:
        st.markdown("#### Debt report")
        query = db.conn.table("player_credits").select("player, remaining_sessions").lt("remaining_sessions", 0).order("remaining_sessions").execute()
        if query.data:
            df_debt = pd.DataFrame(query.data)
            df_debt = df_debt.rename(columns={"player":"Player","remaining_sessions":"Sessions Owed"})
            df_debt["Sessions Owed"] = df_debt["Sessions Owed"].abs()
            st.dataframe(df_debt, use_container_width=True, hide_index=True)
            st.download_button(
                "Download debt report",
                data=create_pdf(df_debt, "JVC — Players In Debt"),
                file_name=f"JVC_Debt_Report_{datetime.now().strftime('%b_%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.success("Everyone is paid up!")

    if show_history_report:
        with rep_col2:
            st.markdown("#### Payment history")
            if not hist_df.empty:
                st.dataframe(hist_df, use_container_width=True, hide_index=True)
                st.download_button(
                    "Download history",
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
            <span class='hero-eyebrow'>Schedule</span>
            <h1 class='hero-title'>Session <span class='hero-accent'>manager</span></h1>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<p class='helper-text' style='margin-bottom:1.25rem'>Sun/Thu practices are generated automatically. Cancel or add custom dates here.</p>", unsafe_allow_html=True)

    overrides      = db.get_schedule_overrides()
    upcoming_list  = get_upcoming_sessions_list(overrides)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown(_section_header("Upcoming schedule", "Next 7 sessions"), unsafe_allow_html=True)
            if upcoming_list:
                for d in upcoming_list[:7]:
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"<div class='session-chip'>{d}</div>", unsafe_allow_html=True)
                    if c2.button("Cancel", type="secondary", key=f"cancel_{d}"):
                        if db.add_schedule_override(d, "Cancelled"):
                            st.rerun()
            else:
                st.info("No upcoming sessions found.")

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(_section_header("Add custom session"), unsafe_allow_html=True)
            st.markdown("<p class='helper-text'>Need a Tuesday practice? Add it here.</p>", unsafe_allow_html=True)
            custom_date = st.date_input("Date")
            if st.button("Add session", use_container_width=True):
                date_str = custom_date.strftime("%b %d")
                if db.add_schedule_override(date_str, "Added"):
                    st.success(f"Added {date_str} to the schedule.")
                    st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown(_section_header("Cancelled sessions", "Removed"), unsafe_allow_html=True)
            cancelled_list = [x['session_date'] for x in overrides if x['status'] == 'Cancelled']
            if cancelled_list:
                for c in cancelled_list:
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"<div class='session-chip cancelled-chip'>{c}</div>", unsafe_allow_html=True)
                    if c2.button("Restore", type="secondary", key=f"restore_{c}"):
                        if db.delete_schedule_override(c):
                            st.rerun()
            else:
                st.markdown("<p class='helper-text'>No sessions currently cancelled.</p>", unsafe_allow_html=True)