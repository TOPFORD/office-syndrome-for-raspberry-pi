import os
import cv2
import mediapipe as mp
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import ttk
import time
import asyncio
import pygame
import subprocess
import sys

# Suppress TensorFlow Lite warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import posture check functions
from posture1 import check_posture1
from posture2L import check_posture2L
from posture2R import check_posture2R
from posture3L import check_posture3L
from posture3R import check_posture3R
from posture4L import check_posture4L
from posture4R import check_posture4R
from posture5L import check_posture5L
from posture5R import check_posture5R
from posture6L import check_posture6L
from posture6R import check_posture6R

# Posture checks configuration
posture_checks = [
    (check_posture1, "ท่าที่ 1", ""),
    (check_posture2R, "ท่าที่ 2", "ข้างขวา"),
    (check_posture2L, "ท่าที่ 2", "ข้างซ้าย"),
    (check_posture3L, "ท่าที่ 3", "ข้างขวา"),
    (check_posture3R, "ท่าที่ 3", "ข้างซ้าย"),
    (check_posture4R, "ท่าที่ 4", "ข้างขวา"),
    (check_posture4L, "ท่าที่ 4", "ข้างซ้าย"),
    (check_posture5R, "ท่าที่ 5", "ข้างขวา"),
    (check_posture5L, "ท่าที่ 5", "ข้างซ้าย"),
    (check_posture6R, "ท่าที่ 6", "ข้างขวา"),
    (check_posture6L, "ท่าที่ 6", "ข้างซ้าย"),
]

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

pygame.init()
try:
    pygame.mixer.music.load("V2.mp3")
except pygame.error:
    print("ไม่พบไฟล์เสียง 'V2.mp3'")

# Global variables
start_time = None
current_pose = 1
target_repeats = 1
current_repeats = 0
is_running = False
body_parts_visible = False

# Tkinter setup
window = tk.Tk()
window.title("Pose Detection")
window.geometry("800x600")
window.configure(bg="#2e2e2e")

def select_repeats(value):
    global target_repeats
    target_repeats = int(value)

def detect_body_parts(results_pose):
    """ตรวจสอบว่ากล้องมองเห็นส่วนหัว ไหล่ แขน และเอวครบหรือไม่"""
    if results_pose and results_pose.pose_landmarks:
        landmarks = results_pose.pose_landmarks.landmark
        required_parts = [
            mp_pose.PoseLandmark.NOSE,
            mp_pose.PoseLandmark.LEFT_SHOULDER,
            mp_pose.PoseLandmark.RIGHT_SHOULDER,
            mp_pose.PoseLandmark.LEFT_HIP,
            mp_pose.PoseLandmark.RIGHT_HIP,
        ]
        for part in required_parts:
            if landmarks[part].visibility < 0.5:
                return False
        return True
    return False

def track_pose(posture_check, results_pose):
    global start_time, current_repeats
    is_correct_pose = False
    if results_pose and results_pose.pose_landmarks:
        try:
            is_correct_pose = posture_check(results_pose)
            if is_correct_pose:
                if start_time is None:
                    start_time = time.time()  # เริ่มจับเวลา
                elif time.time() - start_time >= 2:  # ถือท่าถูกต้องไว้ 2 วินาที
                    current_repeats += 1  # เพิ่มจำนวนครั้งที่ทำสำเร็จ
                    pygame.mixer.music.load("Audio.MP3")  # เล่นเสียงแจ้งเตือน
                    pygame.mixer.music.play()
                    asyncio.sleep(10)
                    start_time = None  # รีเซ็ตเวลา
                    repetition_label.config(text=f"ทำไปแล้ว: {current_repeats} ครั้ง")
                    if current_repeats >= target_repeats:  # ตรวจสอบว่าทำครบจำนวนครั้งหรือยัง
                        current_repeats = 0  # รีเซ็ตจำนวนครั้งสำหรับท่าถัดไป
                        repetition_label.config(text=f"ทำไปแล้ว: {current_repeats} ครั้ง")
                        return True, is_correct_pose
        except Exception as e:
            print(f"Error in posture check: {e}")
    return False, is_correct_pose

def start_pose_detection():
    global is_running, start_time, current_pose, current_repeats, body_parts_visible
    is_running = True
    start_time = None
    current_pose = 1
    current_repeats = 0
    body_parts_visible = False

    if not cap.isOpened():
        status_label.config(text="ไม่สามารถเปิดกล้องได้")
        return
    update_frame()

def update_frame():
    global is_running, current_pose, current_repeats, start_time, body_parts_visible

    if not is_running:
        return

    success, frame = cap.read()
    if not success:
        status_label.config(text="ไม่สามารถอ่านข้อมูลจากกล้องได้")
        return

    frame = cv2.resize(frame, (800, 600))
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_pose = pose.process(image_rgb)

    if not body_parts_visible:
        body_parts_visible = detect_body_parts(results_pose)
        if body_parts_visible:
            status_label.config(text="มองเห็นร่างกายครบแล้ว เริ่มจับท่าทางได้")
        else:
            status_label.config(text="กรุณาอยู่ในเฟรมให้เห็นหัว ไหล่ แขน และเอวครบ")
    else:
        if results_pose.pose_landmarks:
            posture_check, pose_name, side = posture_checks[current_pose - 1]
            pose_complete, is_correct_pose = track_pose(posture_check, results_pose)

            if pose_complete:
                current_pose += 1
                current_repeats = 0
                if current_pose > len(posture_checks):
                    status_label.config(text="ทำท่าครบทุกท่าแล้ว! กำลังเปิดตัวจับเวลา...")
                    window.after(1000, open_completion_timer)
                    return
                else:
                    status_label.config(text=f"{pose_name} {side} ผ่านแล้ว!")
            else:
                status_label.config(text=f"กำลังตรวจจับ: {pose_name} {side}")

            # แสดงจุดข้อต่อบนร่างกาย
            mp_drawing.draw_landmarks(
                frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
            )

    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)

    # เพิ่มเครื่องหมายถูกหรือผิด
    if start_time and body_parts_visible:
        draw.rectangle([(20, 20), (100, 100)], outline="green", width=6)
        draw.line([(30, 70), (55, 90), (90, 40)], fill="green", width=6)  # Checkmark
    else:
        draw.rectangle([(20, 20), (100, 100)], outline="red", width=6)
        draw.line([(30, 30), (90, 90)], fill="red", width=6)  # Cross
        draw.line([(30, 90), (90, 30)], fill="red", width=6)

    imgtk = ImageTk.PhotoImage(image=pil_image)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    window.after(10, update_frame)

def open_completion_timer():
    """เปิดตัวจับเวลาและรีสตาร์ท main.py"""
    window.destroy()
    try:
        subprocess.Popen([sys.executable, "completion_timer.py"])
        time.sleep(5)
        subprocess.Popen([sys.executable, __file__])
    except Exception as e:
        print(f"Error while opening timer or restarting main.py: {e}")

# UI setup
video_label = tk.Label(window)
video_label.pack(fill="both", expand=True)

status_label = tk.Label(window, text="สถานะ: รอเริ่มต้น", bg="#2e2e2e", fg="white", font=("Arial", 20))
status_label.pack(pady=10)

control_frame = tk.Frame(window, bg="#4a4a4a")
control_frame.pack(pady=10)

repetition_label = tk.Label(window, text="ทำไปแล้ว: 0 ครั้ง", bg="#2e2e2e", fg="white", font=("Arial", 20))
repetition_label.pack(pady=10)

start_button = tk.Button(control_frame, text="เริ่ม", command=start_pose_detection, bg="#6ab04c", fg="white")
start_button.grid(row=0, column=0, padx=5)

repeat_selector = ttk.Combobox(control_frame, values=list(range(1, 11)), state="readonly")
repeat_selector.set(1)
repeat_selector.grid(row=0, column=1, padx=5)
repeat_selector.bind("<<ComboboxSelected>>", lambda e: select_repeats(repeat_selector.get()))

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    status_label.config(text="ไม่สามารถเปิดกล้องได้")
    exit()

window.protocol("WM_DELETE_WINDOW", lambda: [cap.release(), window.destroy()])
window.mainloop()
