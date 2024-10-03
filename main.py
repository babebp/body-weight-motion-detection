import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import pandas as pd


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


def main():
    curl_rep = 0
    counting = False
    tasks = [("Push Up", 10), ("Curl", 20)]

    # Initialize MediaPipe Pose
    mp_pose = load_model()
    pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, smooth_landmarks=True)

    st.title("Exercise Tracking")

    col1, col2 = st.columns(2)
    
    with col1.container(height=400):
        time_period = st.selectbox("Time Period", ["Day", "Week", "Month"], index=None ,placeholder="Select Time Period")
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
        st.bar_chart(chart_data)

    with col2.container(height=min(len(tasks)*80, 400)):
        st.subheader("Tasks")
        for i, task in enumerate(tasks):
            st.checkbox(f"{task[0]} - {task[1]} Reps", key=task[0]+str(i))

    st.divider()

    with st.container(height=100):
        left, right = st.columns(2, vertical_alignment="bottom")

        exercise = left.selectbox("Exercise", [" - ".join(map(str, task)) + " " + "Reps" for task in tasks], index=None, placeholder="Select Exercise")
        start_button = right.button("Start")

        target_reps = 2

    if exercise and target_reps and start_button:
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
                cv2.putText(frame, f'Angle: {int(angle)}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Draw progress bar
                draw_progress_bar(frame, angle_percentage)

                # Display curl count
                cv2.putText(frame, f'Curls: {curl_rep}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                if curl_rep >= target_reps:
                    video_placeholder.empty()
                    st.success("Task is Done !")
                    break

            video_placeholder.image(frame, channels="RGB")

if __name__ == "__main__":
    main()
