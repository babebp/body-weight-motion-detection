import streamlit as st
import cv2
import mediapipe as mp
import pandas as pd
import time
from sqlalchemy import text
from streamlit_apexjs import st_apexcharts
import datetime
from workout import track_bicep_curl  # Import the Bicep Curl function

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
    return conn.query(f"SELECT * FROM tasks WHERE status = {status} AND DATE(assign_date) = '{date}';", ttl=0)


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
        curl_rep = 0
        counting = False

        today = datetime.datetime.today().date()
        # today = "2024-10-02 00:00:00"
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
        
        col1, col2, col3 = st.columns(3)
        
        with col1.container(height=550):
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

        with col2.container(height=550):
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
            
        # Track Bicep Curl
        if exercise and "Bicep Curl" in exercise and start_button:
            task_completed = track_bicep_curl(exercise, target_reps, pose, mp_pose)
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
