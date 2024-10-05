import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import pandas as pd
import time
from sqlalchemy import text
from streamlit_apexjs import st_apexcharts
import datetime

st.set_page_config(
    page_title="Exercise Tracking",
    page_icon="🏃‍♂️",
    layout="wide",
)


@st.cache_resource
def load_model():
    return mp.solutions.pose


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Calculate the angle between three points a, b, c"""
    a, b, c = np.array(a), np.array(b), np.array(c)

    # Calculate the angle
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))

    return 360 - angle if angle > 180 else angle


def draw_progress_bar(frame: np.ndarray, angle_percentage: float) -> None:
    """Draws a progress bar on the frame based on the angle percentage."""
    progress_bar_width = 280
    cv2.rectangle(frame, (10, 100), (10 + progress_bar_width, 130), (255, 255, 255), -1)  # Background bar
    progress_bar_length = int(angle_percentage / 100 * progress_bar_width)
    cv2.rectangle(frame, (10, 100), (10 + progress_bar_length, 130), (0, 255, 0), -1)  # Progress bar

# @st.fragment(run_every="2s")
def get_task_names(status):
    conn = st.connection("postgresql", type="sql")
    return conn.query(f'SELECT * FROM tasks WHERE status = {status};', ttl=0)


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

        df = get_task_names(0)
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
            # time_period = st.selectbox("Time Period", ["Day", "Week", "Month"], placeholder="Select Time Period")
            d = st.date_input("Select Date", datetime.date.today())
            chart_data = get_task_names(1)
            options = {
                "chart": {
                    "toolbar": {
                        "show": False
                    }
                },

                "labels": [1991, 1992, 1993, 1994, 1995]
                ,
                "legend": {
                    "show": True,
                    "position": "bottom",
                }
            }
            series = [44, 55, 41, 17, 15]
            st_apexcharts(options, series, 'donut', '400', 'Daily Summary')

        with col2.container(height=550):
            st.subheader("Tasks ❗️", divider=True)
            for i, task in enumerate(tasks_name):
                st.checkbox(task, key=task+str(i), disabled=True)

        st.divider()

        with st.container(height=100):
            left, right = st.columns(2, vertical_alignment="bottom")

            exercise = left.selectbox("Exercise", tasks_name, index=None, placeholder="Select Exercise")
            start_button = right.button("Start", disabled=False if exercise else True)

            if exercise:
                target_reps = int(exercise.split(" ")[-2])

        if exercise:
            st.markdown(
                f"""
                ```
                Exercise Tracking : {exercise}
                ```        
                """)
            
        if exercise and "Push Up" in exercise  and start_button:
            start_time = time.time()
            target_reps = int(target_reps)
            video_placeholder = st.empty()

            cap = cv2.VideoCapture(0)
            while True:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to capture image.")
                    break

                frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process the image and get the pose landmarks
                results = pose.process(frame)

                if exercise and results.pose_landmarks:
                    # Draw landmarks
                    mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                    # Get key points
                    landmarks = results.pose_landmarks.landmark
                    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    # Calculate the angle
                    angle = calculate_angle(shoulder, elbow, wrist)

                    # Calculate the percentage for the progress bar (30 to 90 degrees)
                    angle_percentage = 100 if angle < 30 else (0 if angle > 90 else (90 - angle) / 60 * 100)

                    # Count curls
                    if angle < 30 and counting:
                        curl_rep += 1
                        counting = False
                    elif angle > 80:
                        counting = True

                    # Display the angle
                    cv2.putText(frame, f'Angle: {int(angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # Draw progress bar
                    draw_progress_bar(frame, angle_percentage)

                    # Display curl count
                    cv2.putText(frame, f'Curls: {curl_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
                    # Finish Task
                    if curl_rep >= target_reps:
                        st.session_state.toast_message = 'Task is done! ✅'
                        for key in tasks:
                            if tasks[key] == exercise:
                                conn = st.connection("postgresql", type="sql")
                                tasks_name.remove(exercise)

                                task_id = key  # Replace with your specific task_id
                                update_query = text("UPDATE tasks SET status = 1 WHERE task_id = :task_id")

                                # Execute with SQLAlchemy session
                                with conn.session as s:
                                    s.execute(update_query, {"task_id": task_id})
                                    s.commit()  # Don't forget to commit the changes

                                video_placeholder.empty()
                                st.rerun()
                                break
                        break

                video_placeholder.image(frame, channels="RGB")

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
