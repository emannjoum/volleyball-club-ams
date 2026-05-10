import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database as db
from utils import get_next_session_date, get_upcoming_sessions_list, calculate_streaks, create_pdf

def render_player_dashboard(current_user, radar_label_color):
    st.markdown(f"<h1 class='gradient-text'>Welcome, {current_user.split()[0]}</h1>", unsafe_allow_html=True)
    
    overrides = db.get_schedule_overrides()
    next_session = get_next_session_date(overrides)
    db_data = db.load_attendance()
    stats = db.load_player_stats(current_user)
    
    skill_names = ['Hitting', 'Setting', 'Passing', 'Serving', 'Defense']
    skill_values = [stats['hitting'], stats['setting'], stats['passing'], stats['serving'], stats['defense']]
    top_skill = skill_names[skill_values.index(max(skill_values))]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"<div class='metric-card'><p style='margin:0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase;'>Next Practice</p><h2 style='margin:0; font-weight: 900;'>{next_session}</h2></div>", unsafe_allow_html=True)
        
    with col2:
        current_credits = db.load_player_credits(current_user)
        credit_color = "#059669" if current_credits > 0 else "#dc2626"
        st.markdown(f"<div class='metric-card'><p style='margin:0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase;'>Remaining Sessions</p><h2 style='color: {credit_color} !important; margin:0; font-weight: 900;'>{current_credits} Sessions</h2></div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"<div class='metric-card'><p style='margin:0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase;'>Avg Top Skill</p><h2 style='margin:0; font-weight: 900;'>{top_skill}</h2></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        st.markdown(f"### Check-in for {next_session}")
        
        current_status = db.get_current_attendance_status(current_user, next_session)
        if current_status:
            if current_status == "Available":
                st.markdown(f"Your locked-in status is: <span class='pulse-dot'></span>**<span style='color:green'>Available</span>**", unsafe_allow_html=True)
            else:
                st.markdown(f"Your locked-in status is: **<span style='color:red'>Unavailable</span>**", unsafe_allow_html=True)
        else:
            st.write("Let the coach know if you will be on the court.")
            
        status = st.segmented_control("Your Status", ["Available", "Unavailable"], default=current_status if current_status else "Available")
        if st.button("Update Status", use_container_width=True):
            if db.save_attendance(current_user, status, next_session):
                st.success(f"Status locked in for {next_session}")
                st.rerun()

        st.divider()
        st.markdown("### Players Attendace Streaks")
        if not db_data.empty:
            streak_df = calculate_streaks(db_data)
            max_val = int(streak_df['Max Streak'].max()) if not streak_df.empty else 10
            if max_val == 0: max_val = 1
            
            html_str = "<div>"
            for _, row in streak_df.head(5).iterrows():
                player = row['Player']
                streak = row['Max Streak']
                pct = (streak / max_val * 100)
                html_str += f"<div class='streak-row'><div class='streak-name'>{player}</div><div class='streak-bar-container'><div class='animated-progress'><div class='animated-progress-bar' style='width: {pct}%;'></div></div></div><div class='streak-val'>{streak}</div></div>"
            html_str += "</div>"
            st.markdown(html_str, unsafe_allow_html=True)

    with c2:
        st.markdown("### Your Skill Radar")
        df_skill = pd.DataFrame(dict(r=skill_values, theta=skill_names))
        fig = px.line_polar(df_skill, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#059669', fillcolor='rgba(5, 150, 105, 0.2)')
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=10)),
                angularaxis=dict(visible=True, showticklabels=True, tickfont=dict(size=14, color=radar_label_color, weight="bold"))
            ), 
            showlegend=False, 
            height=400,
            margin=dict(l=80, r=80, t=40, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

def render_player_stats(current_user, grid_empty):
    st.markdown(f"<h1 class='gradient-text'>Season History: {current_user}</h1>", unsafe_allow_html=True)
    db_data = db.load_attendance()
    
    if not db_data.empty:
        user_data = db_data[db_data['player'] == current_user].copy()
        
        user_data['Month'] = user_data['date'].apply(lambda x: x.split(' ')[0])
        # Extract unique months in chronological order, then reverse so the newest is first
        unique_months = list(dict.fromkeys(user_data['Month']))
        unique_months.reverse() 
        available_months = ["All Time"] + unique_months
        
        # Default index to 1 (the newest month) if data exists
        default_idx = 1 if len(available_months) > 1 else 0
        
        filter_col, _ = st.columns([1, 2])
        with filter_col:
            selected_month = st.selectbox("Filter History by Month", available_months, index=default_idx)
            
        if selected_month != "All Time":
            user_data = user_data[user_data['Month'] == selected_month]
        
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

        st.markdown("### Attendance Activity Log")
        sorted_data = user_data.sort_values('created_at') if 'created_at' in user_data.columns else user_data
        squares_html = "<div style='display: flex; flex-wrap: wrap; gap: 4px; padding-top: 10px;'>"
        for idx, row in sorted_data.iterrows():
            color = "#166534" if row['status'] == 'Available' else grid_empty
            squares_html += f"<div class='activity-square' title='{row['date']} - {row['status']}' style='width: 18px; height: 18px; background-color: {color}; border-radius: 3px;'></div>"
        squares_html += "</div>"
        st.markdown(squares_html, unsafe_allow_html=True)
    else:
        st.info("No attendance records found.")

def render_admin():
    st.markdown("<h1 class='gradient-text'>Coach Admin</h1>", unsafe_allow_html=True)
    
    overrides = db.get_schedule_overrides()
    upcoming_date = get_next_session_date(overrides)
    db_data = db.load_attendance()
    players_list = db.load_players()
    
    with st.expander(f"Floor Attendance Override - {upcoming_date}", expanded=False):
        st.write("Manually flip a player's attendance on the floor. Session fees adjust automatically.")
        if players_list:
            override_cols = st.columns(4)
            for i, p in enumerate(players_list):
                col = override_cols[i % 4]
                curr_stat = db.get_current_attendance_status(p, upcoming_date)
                is_avail = (curr_stat == "Available")
                
                changed = col.toggle(f"{p}", value=is_avail, key=f"quick_tgl_{p}")
                if changed != is_avail:
                    new_stat = "Available" if changed else "Unavailable"
                    if db.save_attendance(p, new_stat, upcoming_date):
                        st.rerun()
    st.divider()

    if not db_data.empty:
        upcoming_data = db_data[db_data['date'] == upcoming_date]
        available_players = upcoming_data[upcoming_data['status'] == 'Available']['player'].tolist()
        
        st.markdown(f"### Session Summary: {upcoming_date}")
        col_count, col_names = st.columns([1, 4])
        with col_count:
            st.metric("Total Attending", len(available_players))
        with col_names:
            if available_players:
                st.write("**Confirmed Players:**")
                st.code(", ".join(available_players), language="markdown")
            else:
                st.write("**Confirmed Players:**\nNo players confirmed yet.")
        st.divider()

    tab1, tab2, tab3 = st.tabs(["Attendance Data", "Insert Player Stats", "Manage Roster"])
    
    with tab1:
        if not db_data.empty:
            db_data['Month'] = db_data['date'].apply(lambda x: x.split(' ')[0])
            
            # Extract unique months in chronological order, then reverse so newest is first
            unique_months = list(dict.fromkeys(db_data['Month']))
            unique_months.reverse()
            available_months = ["All Time"] + unique_months
            
            default_idx = 1 if len(available_months) > 1 else 0
            
            matrix_col, _ = st.columns([1, 2])
            with matrix_col:
                selected_matrix_month = st.selectbox("Filter Matrix by Month", available_months, index=default_idx)
                
            filtered_db = db_data if selected_matrix_month == "All Time" else db_data[db_data['Month'] == selected_matrix_month]
            
            if not filtered_db.empty:
                pivot_df = filtered_db.pivot_table(index='player', columns='date', values='status', aggfunc='first').fillna("Unavailable").reset_index()
                st.download_button("Download Clean Attendance PDF", data=create_pdf(pivot_df, f"JVC Attendance Report - {selected_matrix_month}"), file_name="attendance_report.pdf", mime="application/pdf")
                
                def color_matrix(val):
                    if val == 'Available': return 'background-color: #bbf7d0; color: #166534'
                    elif val == 'Unavailable': return 'background-color: #fecaca; color: #991b1b'
                    return ''
                
                display_df = pivot_df.set_index('player')
                styled_df = display_df.style.map(color_matrix) if hasattr(display_df.style, 'map') else display_df.style.applymap(color_matrix)
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.info("No records for this month.")

    with tab2:
        if players_list:
            target = st.selectbox("Select Player", players_list)
            cur_avg = db.load_player_stats(target)
            st.write(f"Current Historical Averages: Hitting ({cur_avg['hitting']}) | Setting ({cur_avg['setting']}) | Passing ({cur_avg['passing']}) | Serving ({cur_avg['serving']}) | Defense ({cur_avg['defense']})")
            
            col1, col2 = st.columns(2)
            with col1:
                h = st.slider("New Hitting Rating", 1, 5, 3)
                s = st.slider("New Setting Rating", 1, 5, 3)
                p = st.slider("New Passing Rating", 1, 5, 3)
            with col2:
                sv = st.slider("New Serving Rating", 1, 5, 3)
                d = st.slider("New Defense Rating", 1, 5, 3)
            if st.button("Log New Evaluation"):
                if db.save_stats(target, h, s, p, sv, d): 
                    st.success("New evaluation logged. Radar average updated.")
        else:
            st.info("Add players in the Manage Roster tab first.")

    with tab3:
        rost_col1, rost_col2 = st.columns(2, gap="large")
        with rost_col1:
            st.subheader("Add New Player")
            with st.form("new_player_form"):
                new_name = st.text_input("Full Name / Display Name")
                new_pos = st.selectbox("Position", ["None", "Outside Hitter", "Middle Blocker", "Setter", "Libero", "Opposite", "Defensive Specialist"])
                if st.form_submit_button("Create Profile"):
                    if new_name:
                        pin = db.add_player(new_name, new_pos)
                        if pin:
                            st.success(f"Added {new_name}. Login PIN is: {pin}")
                            st.rerun()
                    else: st.error("Player name is required.")

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
                        e_name = st.text_input("Name", value=p_data['name'])
                        pos_list = ["None", "Outside Hitter", "Middle Blocker", "Setter", "Libero", "Opposite", "Defensive Specialist"]
                        default_ix = pos_list.index(p_data['position']) if p_data['position'] in pos_list else 0
                        e_pos = st.selectbox("Position", pos_list, index=default_ix)
                        e_pin = st.text_input("PIN Code", value=p_data['access_code'])
                        
                        if st.form_submit_button("Save Changes"):
                            if db.edit_player(edit_target, e_name, e_pos, e_pin):
                                st.success("Player details updated.")
                                st.rerun()
                            
        st.divider()
        st.subheader("Current Roster and Login PINs")
        roster_df = db.get_roster_with_pins()
        if not roster_df.empty:
            roster_df = roster_df.rename(columns={"name": "Player", "position": "Position", "access_code": "Login PIN"})
            st.dataframe(roster_df, use_container_width=True, hide_index=True)

def render_finances(show_history_report):
    st.markdown("<h1 class='gradient-text'>Financial HQ</h1>", unsafe_allow_html=True)
    
    current_month = datetime.now().strftime('%b %Y')
    hist_df = db.load_payment_history()
    
    month_sessions = 0
    if not hist_df.empty:
        hist_df['is_current_month'] = hist_df['Date'].str.contains(datetime.now().strftime('%b'))
        month_sessions = hist_df[hist_df['is_current_month']]['Sessions Added'].sum()

    st.metric(f"Total Sessions Purchased This Month ({current_month})", month_sessions)
    st.divider()
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    players_list = db.load_players()
    
    with col1:
        st.subheader("Record Payment")
        if players_list:
            with st.form("payment_form"):
                target_player = st.selectbox("Select Player", players_list)
                plan_type = st.radio("Payment Plan Type", ["Monthly (8 Sessions)", "Daily (1 Session)", "Custom Number"])
                custom_amount = st.number_input("Enter custom number of sessions", min_value=-50, max_value=50, value=0)
                
                if st.form_submit_button("Confirm Payment"):
                    sessions_to_add = 8 if plan_type == "Monthly (8 Sessions)" else (1 if plan_type == "Daily (1 Session)" else custom_amount)
                    if db.update_player_credits(target_player, sessions_to_add, plan_type):
                        st.success(f"Payment recorded. {sessions_to_add} session(s) added to {target_player}.")
                        st.rerun()
        else:
            st.info("No players available.")

    with col2:
        overrides = db.get_schedule_overrides()
        upcoming_date = get_next_session_date(overrides)
        st.subheader(f"Payments for {upcoming_date}")
        
        try:
            att_query = db.conn.table("attendance").select("player").eq("date", upcoming_date).eq("status", "Available").execute()
            if att_query.data:
                attendees = [row['player'] for row in att_query.data]
                cred_query = db.conn.table("player_credits").select("player, remaining_sessions").execute()
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
    if show_history_report:
        rep_col1, rep_col2 = st.columns(2, gap="large")
    else:
        rep_col1, rep_col2 = st.columns([1, 1]) 
        
    with rep_col1:
        st.markdown("### Debt Report")
        query = db.conn.table("player_credits").select("player, remaining_sessions").lt("remaining_sessions", 0).order("remaining_sessions").execute()
        if query.data:
            df_debt = pd.DataFrame(query.data)
            df_debt = df_debt.rename(columns={"player": "Player", "remaining_sessions": "Sessions Owed"})
            df_debt["Sessions Owed"] = df_debt["Sessions Owed"].abs() 
            st.dataframe(df_debt, use_container_width=True, hide_index=True)
            
            st.download_button("Download Debt Report (PDF)", data=create_pdf(df_debt, "JVC - Players In Debt Report"), file_name=f"JVC_Debt_Report_{datetime.now().strftime('%b_%d')}.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.success("Everyone is paid up.")
            
    if show_history_report:
        with rep_col2:
            st.markdown("### Payment History")
            if not hist_df.empty:
                st.dataframe(hist_df, use_container_width=True, hide_index=True)
                st.download_button("Download Payment History (PDF)", data=create_pdf(hist_df, "JVC - Payment Transaction Log"), file_name=f"JVC_Payment_History_{datetime.now().strftime('%b_%d')}.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.info("No payment transactions recorded yet.")

def render_session_manager():
    st.markdown("<h1 class='gradient-text'>Session Manager</h1>", unsafe_allow_html=True)
    st.write("Control the team's schedule. Auto-generated Sunday/Thursday practices will appear here. You can cancel them or add custom match/practice dates.")
    
    overrides = db.get_schedule_overrides()
    upcoming_list = get_upcoming_sessions_list(overrides)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### Upcoming Schedule")
        if upcoming_list:
            for d in upcoming_list[:7]:
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{d}**")
                if c2.button("Cancel", key=f"cancel_{d}"):
                    if db.add_schedule_override(d, "Cancelled"):
                        st.rerun()
        else:
            st.info("No upcoming sessions found.")
            
        st.divider()
        st.markdown("### Add Custom Session")
        st.write("Need a practice on a Tuesday? Add it here.")
        custom_date = st.date_input("Select Date")
        if st.button("Add Session"):
            date_str = custom_date.strftime("%b %d")
            if db.add_schedule_override(date_str, "Added"):
                st.success(f"Added {date_str} to the schedule.")
                st.rerun()

    with col2:
        st.markdown("### Cancelled Sessions")
        cancelled_list = [x['session_date'] for x in overrides if x['status'] == 'Cancelled']
        if cancelled_list:
            for c in cancelled_list:
                c1, c2 = st.columns([3, 1])
                c1.write(f"~~{c}~~")
                if c2.button("Restore", key=f"restore_{c}"):
                    if db.delete_schedule_override(c):
                        st.rerun()
        else:
            st.write("No sessions currently cancelled.")