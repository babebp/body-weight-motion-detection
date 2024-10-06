import streamlit as st
import cv2
import mediapipe as mp
import pandas as pd
import time
from sqlalchemy import text
from streamlit_apexjs import st_apexcharts
import datetime
from workout import EXCERCISE_FUNCTIONS,track_bicep_curl,track_push_up,track_leg_press   # Import the Bicep Curl function

st.set_page_config(
    page_title="Exercise Tracking",
    page_icon="🏃‍♂️",
    layout="wide",
)

@st.cache_resource
def load_model():
    return mp.solutions.pose

# @st.fragment(run_every="2s")
def get_task_names(status, date):
    conn = st.connection("postgresql", type="sql")
    query_sql = conn.query(f"SELECT * FROM tasks WHERE status = {status} AND DATE(assign_date) = '{date}';", ttl=0)
    return query_sql

# ฟังก์ชันใหม่สำหรับ Query ข้อมูลย้อนหลัง
def get_historical_task_data(status, start_date, end_date):
    conn = st.connection("postgresql", type="sql")
    query_sql = conn.query(f"SELECT * FROM tasks WHERE status = {status} AND assign_date BETWEEN '{start_date}' AND '{end_date}';", ttl=0)
    return query_sql

def main():
    st.title("Exercise Tracking")
    tab1, tab2 = st.tabs(['Main', 'About'])

    if 'toast_message' not in st.session_state:
        st.session_state.toast_message = None

    # Display the toast message if it exists
    if st.session_state.toast_message:
        st.toast(st.session_state.toast_message)
        st.session_state.toast_message = None

    with tab1:
        today = datetime.datetime.today().date()
        # today = "2024-10-02 00:00:00" #Dont Remove This
        # today = datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
        df = get_task_names(0, today)
        tasks = {}
        tasks_name = []

        for row in df.itertuples():
            task_name = f"{row.exercise} - {row.reps} Reps"
            tasks_name.append(task_name)
            tasks[row.task_id] = task_name

        # Initialize MediaPipe Pose
        mp_pose = load_model()
        pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, smooth_landmarks=True)

        with st.container(height=250):
            st.markdown(
                """
                ### Note 💡
                ```
                1. Track your progress and celebrate achievements as you complete exercises. ✅

                2. Choose exercises tailored to your goals, with easy tracking and management. ✅

                3. Monitor your performance and adjust routines for sustained improvement. ✅

                ```
                """
            )
        
        col1, col2, col3 = st.columns([2, 2, 1])  # Adjust to 3 columns for placing two charts and tasks
        
        with col1.container(height=550):
            st.subheader("Daily Summary")
            d = st.date_input("Select Date", datetime.date.today())
            chart_data = get_task_names(1, d)
            chart_data['date'] = pd.to_datetime(chart_data['assign_date']).dt.date

            # Group by date and pivot the exercises into columns
            result = chart_data.pivot_table(columns='exercise', values='reps', aggfunc='sum', fill_value=0)

            options = {
                "chart": {
                    "toolbar": {
                        "show": False
                    }
                },
                "labels": result.columns.to_list(),
                "legend": {
                    "show": True,
                    "position": "right",
                }
            }
            series = result.iloc[0].to_list()
            st_apexcharts(options, series, 'donut', '470', 'Daily Summary')

        # Historical Summary Bar Chart
        with col2.container(height=550):
            st.subheader("Exercise Summary")
            # Set default start_date as beginning of the month and end_date as today - 1
            col_start, col_end = st.columns(2)

            with col_start:
                start_date = st.date_input("Start Date", value=today.replace(day=1))
            
            with col_end:
                end_date = st.date_input("End Date", value=today - datetime.timedelta(days=1))

            # Fetch historical data
            historical_data = get_historical_task_data(1, start_date, end_date)
            historical_data['date'] = pd.to_datetime(historical_data['assign_date']).dt.date

            # Group by exercise and sum the reps for each exercise
            historical_summary = historical_data.groupby('exercise')['reps'].sum().reset_index()

            # Prepare data for the bar chart
            bar_options = {
                "chart": {
                    "type": "bar",
                    "toolbar": {
                        "show": False
                    }
                },
                "plotOptions": {
                    "bar": {
                        "horizontal": False,
                        "columnWidth": "55%",
                    }
                },
                "dataLabels": {
                    "enabled": False
                },
                "xaxis": {
                    "categories": historical_summary['exercise'].tolist(),
                },
                "tooltip": {
                    "theme": "dark",  # This will change the tooltip to a light theme with black text
                },
                "legend": {
                    "show": True,
                    "position": "bottom",
                },
            }

            bar_series = [{
                "name": "Reps",
                "data": historical_summary['reps'].tolist()
            }]

            st_apexcharts(bar_options, bar_series, 'bar', '470', 'Exercise Summary')

        # Tasks List
        with col3.container(height=550):
            st.subheader("Tasks ❗️", divider=True)
            for i, task in enumerate(tasks_name):
                st.checkbox(task, key=task+str(i), disabled=True)

        st.divider()

        with st.container(height=100):
            left, middle, right = st.columns(3, vertical_alignment="bottom")

            exercise = left.selectbox("Exercise", tasks_name, index=None, placeholder="Select Exercise")
            start_button = middle.button("Start", disabled=False if exercise else True)
            stop_button = right.button("Stop", disabled=False if exercise else True)

            if exercise:
                target_reps = int(exercise.split(" ")[-2])

        if exercise:
            st.markdown(
                f"""
                ```
                Exercise Tracking : {exercise}
                ```        
                """)
            
        if exercise and start_button:
            # Loop through the available exercises and track if match is found
            for exercise_name, track_function in EXCERCISE_FUNCTIONS.items():
                if exercise_name in exercise:
                    task_completed = track_function(exercise, target_reps, pose, mp_pose)
                    if task_completed:
                        # Update the task status in the database
                        for key in tasks:
                            if tasks[key] == exercise:
                                conn = st.connection("postgresql", type="sql")
                                tasks_name.remove(exercise)

                                task_id = key
                                update_query = text("UPDATE tasks SET status = 1 WHERE task_id = :task_id")

                                with conn.session as s:
                                    s.execute(update_query, {"task_id": task_id})
                                    s.commit()

                        st.rerun()

    with tab2:
        st.markdown(
            """ 
            ``` 
            Jaturawich Khochun 6410110060 
            ``` 
            ``` 
            Pacharawut Thanawut 6410110340 
            ``` 
            """)

if __name__ == "__main__":
    main()
