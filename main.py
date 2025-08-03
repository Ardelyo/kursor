import cv2
import time
import pyautogui
import tkinter as tk
import threading
import queue
from kursor.config import config_manager
from kursor.tracking.tracker import HandTracker, FaceTracker
from kursor.input.mouse_handler import MouseHandler
from kursor.input.virtual_keyboard import VirtualKeyboard
from kursor.gui.main_gui import MainGUI
from kursor.gui.gui_settings import SettingsGUI
from ttkthemes import ThemedTk

class CVThread(threading.Thread):
    def __init__(self, app, frame_queue, result_queue):
        super().__init__(daemon=True)
        self.app = app
        self.frame_queue = frame_queue
        self.result_queue = result_queue
        self.hand_tracker = HandTracker()
        self.face_tracker = FaceTracker()

    def run(self):
        while True:
            frame = self.frame_queue.get()
            if frame is None: # Sentinel for stopping
                break

            processed_frame, gesture, pointer = self.process_frame(frame)
            self.result_queue.put((processed_frame, gesture, pointer))

    def process_frame(self, frame):
        gesture = None
        pointer = (-1, -1)
        if self.app.control_mode == "hand":
            frame, _ = self.hand_tracker.find_hands(frame)
            if self.app.mouse_control_active and self.hand_tracker.landmark_list:
                gesture = self.hand_tracker.get_gestures()
                pointer, _ = self.hand_tracker.get_landmark_position()
        else: # Face mode
            frame, _ = self.face_tracker.find_faces(frame)
            if self.app.mouse_control_active and self.face_tracker.raw_face_landmarks:
                gesture = self.face_tracker.get_face_gestures(frame)
                pointer = self.face_tracker.get_landmark_position(frame)
        return frame, gesture, pointer

class Application:
    def __init__(self, root):
        self.root = root
        self.settings = config_manager.load_settings()

        self.main_gui = MainGUI(root, self)
        self.mouse_handler = MouseHandler(pyautogui.size()[0], pyautogui.size()[1])
        self.vkeyboard = VirtualKeyboard()

        self.control_mode = self.settings.get("control_mode", "hand")
        self.mouse_control_active = False

        self.frame_queue = queue.Queue(maxsize=1)
        self.result_queue = queue.Queue(maxsize=1)
        self.cv_thread = CVThread(self, self.frame_queue, self.result_queue)
        self.cv_thread.start()

        self.cap = cv2.VideoCapture(self.settings.get("camera_index", 0))
        self.update_camera_feed()
        self.process_results()

    def toggle_mouse_control(self):
        self.mouse_control_active = not self.mouse_control_active
        self.main_gui.update_status(self.control_mode, self.mouse_control_active)

    def switch_control_mode(self):
        self.control_mode = "face" if self.control_mode == "hand" else "hand"
        self.main_gui.update_status(self.control_mode, self.mouse_control_active)

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        SettingsGUI(settings_window).pack(expand=True, fill=tk.BOTH)

    def update_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            if not self.frame_queue.full():
                self.frame_queue.put(cv2.flip(frame, 1))
        self.root.after(10, self.update_camera_feed)

    def process_results(self):
        try:
            frame, gesture, pointer = self.result_queue.get_nowait()
            self.main_gui.update_video_feed(frame)
            if gesture:
                self.handle_gesture(gesture, pointer)
        except queue.Empty:
            pass
        self.root.after(10, self.process_results)

    def handle_gesture(self, gesture, pointer):
        cam_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        cam_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.mouse_handler.move_mouse(pointer[0], pointer[1], cam_width, cam_height)

        if self.control_mode == "hand":
            if gesture.get("left_click"):
                self.mouse_handler.left_click()
        else: # Face mode
            if gesture.get("left_blink_detected"):
                self.mouse_handler.left_click()

    def on_closing(self):
        self.frame_queue.put(None) # Stop CV thread
        self.cv_thread.join()
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = Application(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()