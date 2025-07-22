
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

class MainGUI(tk.Frame):
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.master = master
        self.app_controller = app_controller
        self.master.title("Kursor - Gesture Control")

        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Left panel for controls
        control_panel = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.mode_label = ttk.Label(control_panel, text="Mode: Hand")
        self.mode_label.pack(pady=5)

        self.status_label = ttk.Label(control_panel, text="Status: Inactive")
        self.status_label.pack(pady=5)

        self.start_stop_button = ttk.Button(control_panel, text="Start", command=self.app_controller.toggle_mouse_control)
        self.start_stop_button.pack(pady=10, fill=tk.X)

        self.switch_mode_button = ttk.Button(control_panel, text="Switch to Face Mode", command=self.app_controller.switch_control_mode)
        self.switch_mode_button.pack(pady=10, fill=tk.X)

        self.settings_button = ttk.Button(control_panel, text="Settings", command=self.app_controller.open_settings)
        self.settings_button.pack(pady=10, fill=tk.X)

        self.quit_button = ttk.Button(control_panel, text="Quit", command=self.master.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

        # Right panel for camera feed
        self.camera_label = ttk.Label(main_frame)
        self.camera_label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

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
    # This is for testing the GUI layout independently
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
