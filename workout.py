# work_out.py
import cv2
import time
import numpy as np
import mediapipe as mp
import streamlit as st
from sqlalchemy import text

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


def track_bicep_curl(exercise, target_reps, pose, mp_pose):
    """Track Bicep Curl using MediaPipe pose estimation"""
    curl_rep = 0
    counting = False
    start_time = time.time()
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
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed


def track_push_up(exercise, target_reps, pose, mp_pose):
    """Track Push Up using MediaPipe pose estimation"""
    push_up_rep = 0
    counting = False
    start_time = time.time()
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

            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate the angles
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            hip_angle = calculate_angle(shoulder, hip, knee)

            # Count push ups based on elbow angle
            if elbow_angle < 70 and counting:
                push_up_rep += 1
                counting = False
            elif elbow_angle > 160:
                counting = True

            # Display the angles
            cv2.putText(frame, f'Elbow Angle: {int(elbow_angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Hip Angle: {int(hip_angle)}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Display push up count
            cv2.putText(frame, f'Push Ups: {push_up_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task
            if push_up_rep >= target_reps:
                st.session_state.toast_message = 'Task is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed

def track_leg_press(exercise, target_reps, pose, mp_pose):
    """Track Leg Press using MediaPipe pose estimation"""
    leg_press_rep = 0
    counting = False
    start_time = time.time()
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
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate the angle
            knee_angle = calculate_angle(hip, knee, ankle)

            # Count leg presses based on knee angle
            if knee_angle < 70 and counting:
                leg_press_rep += 1
                counting = False
            elif knee_angle > 160:
                counting = True

            # Display the angle
            cv2.putText(frame, f'Knee Angle: {int(knee_angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Display leg press count
            cv2.putText(frame, f'Leg Presses: {leg_press_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task
            if leg_press_rep >= target_reps:
                st.session_state.toast_message = 'Task is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed

def track_plank(exercise, target_reps, pose, mp_pose):
    """Track Plank using MediaPipe pose estimation"""
    plank_time = 0
    start_time = time.time()
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
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate the angle at the hip
            hip_angle = calculate_angle(shoulder, hip, ankle)

            # Check if the angle is within the plank position range (e.g., 150-180 degrees)
            if 150 <= hip_angle <= 180:
                plank_time = time.time() - start_time

            # Display the hip angle
            cv2.putText(frame, f'Hip Angle: {int(hip_angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Display plank time
            cv2.putText(frame, f'Plank Time: {int(plank_time)} seconds', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task if user has held the plank for the target time (e.g., target_reps as seconds)
            if plank_time >= target_reps:
                st.session_state.toast_message = 'Plank is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed

def track_tricep_dip(exercise, target_reps, pose, mp_pose):
    """Track Tricep Dip using MediaPipe pose estimation"""
    dip_rep = 0
    counting = False
    start_time = time.time()
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
            angle_percentage = 100 if angle < 60 else (0 if angle > 120 else (120 - angle) / 60 * 100)

            # Count dips
            if angle < 60 and counting:
                dip_rep += 1
                counting = False
            elif angle > 120:
                counting = True

            # Display the angle
            cv2.putText(frame, f'Angle: {int(angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Display rep count
            cv2.putText(frame, f'Dips: {dip_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task
            if dip_rep >= target_reps:
                st.session_state.toast_message = 'Task is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed

def track_squat(exercise, target_reps, pose, mp_pose):
    """Track Squat using MediaPipe pose estimation"""
    squat_rep = 0
    counting = False
    start_time = time.time()
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
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate the angle
            knee_angle = calculate_angle(hip, knee, ankle)

            # Count squats based on knee angle
            if knee_angle < 70 and counting:
                squat_rep += 1
                counting = False
            elif knee_angle > 160:
                counting = True

            # Display the angle
            cv2.putText(frame, f'Knee Angle: {int(knee_angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Display squat count
            cv2.putText(frame, f'Squats: {squat_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task
            if squat_rep >= target_reps:
                st.session_state.toast_message = 'Task is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed

def track_burpee(exercise, target_reps, pose, mp_pose):
    """Track Burpee using MediaPipe pose estimation"""
    burpee_rep = 0
    counting = False
    start_time = time.time()
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
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate the angle
            knee_angle = calculate_angle(hip, knee, ankle)

            # Count burpees based on knee angle and motion
            if knee_angle < 70 and counting:
                burpee_rep += 1
                counting = False
            elif knee_angle > 160:
                counting = True

            # Display the angle
            cv2.putText(frame, f'Knee Angle: {int(knee_angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Display burpee count
            cv2.putText(frame, f'Burpees: {burpee_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task
            if burpee_rep >= target_reps:
                st.session_state.toast_message = 'Task is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed

def track_pull_up(exercise, target_reps, pose, mp_pose):
    """Track Pull-Up using MediaPipe pose estimation"""
    pull_up_rep = 0
    counting = False
    start_time = time.time()
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

            # Count pull-ups
            if angle < 30 and counting:
                pull_up_rep += 1
                counting = False
            elif angle > 80:
                counting = True

            # Display the angle
            cv2.putText(frame, f'Angle: {int(angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Draw progress bar
            draw_progress_bar(frame, angle_percentage)

            # Display pull-up count
            cv2.putText(frame, f'Pull-Ups: {pull_up_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task
            if pull_up_rep >= target_reps:
                st.session_state.toast_message = 'Task is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed
def track_lunge(exercise, target_reps, pose, mp_pose):
    """Track Lunge using MediaPipe pose estimation"""
    lunge_rep = 0
    counting = False
    start_time = time.time()
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
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate the angle
            knee_angle = calculate_angle(hip, knee, ankle)

            # Calculate the percentage for the progress bar (30 to 90 degrees)
            angle_percentage = 100 if knee_angle < 70 else (0 if knee_angle > 160 else (160 - knee_angle) / 90 * 100)

            # Count lunges based on knee angle
            if knee_angle < 70 and counting:
                lunge_rep += 1
                counting = False
            elif knee_angle > 160:
                counting = True

            # Display the angle
            cv2.putText(frame, f'Knee Angle: {int(knee_angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Draw progress bar
            draw_progress_bar(frame, angle_percentage)

            # Display lunge count
            cv2.putText(frame, f'Lunges: {lunge_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task
            if lunge_rep >= target_reps:
                st.session_state.toast_message = 'Task is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed

def track_bench_press(exercise, target_reps, pose, mp_pose):
    """Track Bench Press using MediaPipe pose estimation"""
    bench_press_rep = 0
    counting = False
    start_time = time.time()
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
            elbow_angle = calculate_angle(shoulder, elbow, wrist)

            # Calculate the percentage for the progress bar (30 to 90 degrees)
            angle_percentage = 100 if elbow_angle < 60 else (0 if elbow_angle > 160 else (160 - elbow_angle) / 100 * 100)

            # Count bench presses based on elbow angle
            if elbow_angle < 60 and counting:
                bench_press_rep += 1
                counting = False
            elif elbow_angle > 160:
                counting = True

            # Display the angle
            cv2.putText(frame, f'Elbow Angle: {int(elbow_angle)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Draw progress bar
            draw_progress_bar(frame, angle_percentage)

            # Display bench press count
            cv2.putText(frame, f'Bench Presses: {bench_press_rep}/{target_reps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Time: {time.time() - start_time}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Finish Task
            if bench_press_rep >= target_reps:
                st.session_state.toast_message = 'Task is done! ✅'
                return True  # Task is completed

        video_placeholder.image(frame, channels="RGB")

    return False  # Task is not completed


# Mapping between exercise names and tracking functions
EXCERCISE_FUNCTIONS = {
    "Bicep Curl": track_bicep_curl,
    "Push Up": track_push_up,
    "Leg Press": track_leg_press,
    "Plank": track_plank,
    "Tricep Dip": track_tricep_dip,
    "Squat": track_squat,
    "Burpee": track_burpee,
    "Pull-Up": track_pull_up,
    "Lunge": track_lunge,
    "Bench Press": track_bench_press,
}

