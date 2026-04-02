import streamlit as st
import pandas as pd
import numpy as np
from st_supabase_connection import SupabaseConnection

st.subheader("Practice Check-in")
status = st.segmented_control(
    "Your Status for April 4th:", # maybe add cols and move to the middle
    options=["In","Out"],
    default="Out",
    key="attendance_status"
)

if status == "In":
    st.toast("Attendance logged, See you at 4 PM!", icon='🏐')

st.divider()

# if from_db_attendance > 5: st.balloons()
with st.sidebar:
    st.image("https://via.placeholder.com/150", caption="Club Name") 
    app_mode = st.radio("Go to:", ["My Check-in", "Team Analytics", "Finance Tracker"])
    st.divider()
    if st.button("Log Out"):
        st.rerun()

with st.container(border=True):
    st.write("### 🏐 Your Progress")
    col1, col2 = st.columns(2)
    col1.metric("Attendance", "92%", "+3%")
    col2.metric("Fees", "Paid", "April")

chart_data = pd.DataFrame({
    "Player": ["Lina", "Sara", "Mayar", "Haya", "Noor"],
    "Sessions": [12, 8, 15, 10, 5]
})


st.write("### Team Attendance (Monthly)")
plot_colour = '#C48FDC'
st.bar_chart(chart_data, x="Player", y="Sessions", color=plot_colour)

"""conn = st.connection("supabase",type=SupabaseConnection)

rows = conn.query("*", table="mytable", ttl="10m").execute()

for row in rows.data:
    st.write(f"{row['name']} has a :{row['pet']}:")
"""
user_name = st.text_input("enter your name", key = "name")

add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone') # will delete, only exp sidebar
)

add_slider = st.sidebar.slider( # will delete
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0)
)

left_column, middle_column, right_column = st.columns(3) # no need currently
middle_column.button('Press me!')

with right_column:
    chosen = st.radio(
        'Sorting hat',
        ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
    st.write(f"You are in {chosen} house!")

st.header(f"Hi,{user_name}")
st.divider()
prac_status = ["Out", "In"]
game_status = ["Out", "In", "Arrive Late", "Leave Early"]

'Are you going to attend April 4th practice?'
player_status = st.selectbox("Player's Status", prac_status)

color=st.color_picker("Pikc", "#46B290")

df = pd.DataFrame(np.random.randn(20,3), columns=['x', 'y', 'z'])

if df not in st.session_state:
    st.session_state.df = df
st.scatter_chart(st.session_state.df,x="x", y="y", color=color)
# data for all users > cache a function that retrieves that data
# personal data > save in session state