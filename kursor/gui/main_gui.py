import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from ttkthemes import ThemedTk

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

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Control Tab
        control_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(control_tab, text="Controls")
        self.create_control_tab(control_tab)

        # Camera Tab
        camera_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(camera_tab, text="Camera Feed")
        self.create_camera_tab(camera_tab)

        # Status Bar
        self.status_bar = ttk.Frame(self.master, padding="5")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.mode_label = ttk.Label(self.status_bar, text="Mode: Hand")
        self.mode_label.pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(self.status_bar, text="Status: Inactive")
        self.status_label.pack(side=tk.LEFT, padx=5)

    def create_control_tab(self, parent):
        self.start_stop_button = ttk.Button(parent, text="Start", command=self.app_controller.toggle_mouse_control)
        self.start_stop_button.pack(pady=10, fill=tk.X)

        self.switch_mode_button = ttk.Button(parent, text="Switch to Face Mode", command=self.app_controller.switch_control_mode)
        self.switch_mode_button.pack(pady=10, fill=tk.X)

        self.settings_button = ttk.Button(parent, text="Settings", command=self.app_controller.open_settings)
        self.settings_button.pack(pady=10, fill=tk.X)

        self.quit_button = ttk.Button(parent, text="Quit", command=self.master.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

    def create_camera_tab(self, parent):
        self.camera_label = ttk.Label(parent)
        self.camera_label.pack(expand=True, fill=tk.BOTH)

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

    root = ThemedTk(theme="arc")
    app = MainGUI(root, MockAppController())
    root.mainloop()