import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from .theme import apply_theme

class MainGUI(tk.Frame):
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.master = master
        self.app_controller = app_controller
        self.master.title("Kursor - Gesture Control")
        self.master.geometry("800x600")

        apply_theme(self.master)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.create_control_panel(left_panel)
        self.create_camera_feed(right_panel)
        self.create_status_bar(self.master)

    def create_control_panel(self, parent):
        parent.pack_propagate(False)
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.pack(expand=True, fill=tk.BOTH)

        self.start_stop_button = ttk.Button(control_frame, text="Start", command=self.app_controller.toggle_mouse_control)
        self.start_stop_button.pack(pady=10, fill=tk.X)

        self.switch_mode_button = ttk.Button(control_frame, text="Switch to Face Mode", command=self.app_controller.switch_control_mode)
        self.switch_mode_button.pack(pady=10, fill=tk.X)

        self.settings_button = ttk.Button(control_frame, text="Settings", command=self.app_controller.open_settings)
        self.settings_button.pack(pady=10, fill=tk.X)

        self.quit_button = ttk.Button(control_frame, text="Quit", command=self.master.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

    def create_camera_feed(self, parent):
        camera_frame = ttk.LabelFrame(parent, text="Camera Feed", padding="10")
        camera_frame.pack(expand=True, fill=tk.BOTH)
        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.pack(expand=True, fill=tk.BOTH)

    def create_status_bar(self, parent):
        status_bar = ttk.Frame(parent, padding="5")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.mode_label = ttk.Label(status_bar, text="Mode: Hand")
        self.mode_label.pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_bar, text="Status: Inactive")
        self.status_label.pack(side=tk.LEFT, padx=5)

    def update_video_feed(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)

    def update_status(self, mode, is_active):
        self.mode_label.config(text=f"Mode: {mode.capitalize()}")
        self.status_label.config(text=f"Status: {'Active' if is_active else 'Inactive'}")
        self.start_stop_button.config(text="Stop" if is_active else "Start")
        self.switch_mode_button.config(text=f"Switch to {'Hand' if mode == 'face' else 'Face'} Mode")

if __name__ == '__main__':
    class MockAppController:
        def toggle_mouse_control(self):
            print("Toggle mouse control")
        def switch_control_mode(self):
            print("Switch control mode")
        def open_settings(self):
            print("Open settings")

    root = tk.Tk()
    app = MainGUI(root, MockAppController())
    root.mainloop()