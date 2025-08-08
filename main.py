import tkinter as tk
from kursor.gui.main_gui import MainGUI
from kursor.gui.gui_settings import SettingsGUI
from kursor.input.mouse_handler import MouseHandler
from kursor.tracking.tracker import Tracker
from kursor.config.config_manager import load_settings, save_settings
import cv2
import threading
import queue

class AppController:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.mouse_handler = MouseHandler(self.settings)
        self.tracker = Tracker(self.settings, self.mouse_handler)
        self.main_gui = MainGUI(self.root, self)
        self.is_mouse_control_active = False

        self.frame_queue = queue.Queue(maxsize=1)
        self.result_queue = queue.Queue(maxsize=1)
        self.cv_thread = threading.Thread(target=self.run_tracker, daemon=True)
        self.cv_thread.start()

        self.cap = cv2.VideoCapture(self.settings.get("camera_index", 0))
        self.update_camera_feed()
        self.process_results()

        self.update_gui_status()

    def run_tracker(self):
        while True:
            frame = self.frame_queue.get()
            if frame is None:
                break
            processed_frame, gesture, pointer = self.tracker.process_frame(frame)
            self.result_queue.put((processed_frame, gesture, pointer))

    def toggle_mouse_control(self):
        self.is_mouse_control_active = not self.is_mouse_control_active
        self.update_gui_status()

    def switch_control_mode(self):
        current_mode = self.settings.get("control_mode", "hand")
        new_mode = "face" if current_mode == "hand" else "hand"
        self.settings["control_mode"] = new_mode
        save_settings(self.settings)
        self.tracker.update_settings(self.settings)
        self.update_gui_status()

    def open_settings(self):
        settings_window = SettingsGUI(self.root)
        self.root.wait_window(settings_window)
        self.settings = load_settings()
        self.tracker.update_settings(self.settings)

    def update_gui_status(self):
        mode = self.settings.get("control_mode", "hand")
        self.main_gui.update_status(mode, self.is_mouse_control_active)

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
            if self.is_mouse_control_active and gesture:
                self.mouse_handler.handle_gesture(gesture, pointer)
        except queue.Empty:
            pass
        self.root.after(10, self.process_results)

    def on_closing(self):
        self.frame_queue.put(None)
        self.cv_thread.join()
        self.cap.release()
        self.root.destroy()

    def run(self):
        self.main_gui.pack(expand=True, fill=tk.BOTH)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppController(root)
    app.run()