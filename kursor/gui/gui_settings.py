import tkinter as tk
from tkinter import ttk, messagebox
from kursor.config import config_manager
from .theme import apply_theme

class SettingsGUI(tk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Settings")
        self.geometry("500x400")
        apply_theme(self)

        self.settings = config_manager.load_settings()

        self.create_widgets()
        self.load_settings_to_gui()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill=tk.BOTH)

        general_tab = ttk.Frame(notebook, padding="10")
        notebook.add(general_tab, text="General")
        self.create_general_tab(general_tab)

        hand_tab = ttk.Frame(notebook, padding="10")
        notebook.add(hand_tab, text="Hand Tracking")
        self.create_hand_tab(hand_tab)

        face_tab = ttk.Frame(notebook, padding="10")
        notebook.add(face_tab, text="Face Tracking")
        self.create_face_tab(face_tab)

        gestures_tab = ttk.Frame(notebook, padding="10")
        notebook.add(gestures_tab, text="Gestures")
        self.create_gestures_tab(gestures_tab)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings)
        save_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def create_general_tab(self, parent):
        mode_frame = ttk.LabelFrame(parent, text="Control Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=5)
        self.control_mode_var = tk.StringVar(value=self.settings.get("control_mode"))
        ttk.Radiobutton(mode_frame, text="Hand", variable=self.control_mode_var, value="hand").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Face", variable=self.control_mode_var, value="face").pack(side=tk.LEFT, padx=5)

        sensitivity_frame = ttk.LabelFrame(parent, text="Mouse Sensitivity", padding="10")
        sensitivity_frame.pack(fill=tk.X, pady=5)
        self.sensitivity_var = tk.DoubleVar(value=self.settings.get("mouse_sensitivity"))
        ttk.Scale(sensitivity_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, variable=self.sensitivity_var).pack(fill=tk.X)

    def create_hand_tab(self, parent):
        click_threshold_frame = ttk.LabelFrame(parent, text="Click Threshold Distance", padding="10")
        click_threshold_frame.pack(fill=tk.X, pady=5)
        self.click_threshold_var = tk.IntVar(value=self.settings.get("hand_gestures", {}).get("click_threshold"))
        ttk.Scale(click_threshold_frame, from_=10, to=100, orient=tk.HORIZONTAL, variable=self.click_threshold_var).pack(fill=tk.X)

    def create_face_tab(self, parent):
        ear_threshold_frame = ttk.LabelFrame(parent, text="Eye Aspect Ratio (EAR) Threshold", padding="10")
        ear_threshold_frame.pack(fill=tk.X, pady=5)
        self.ear_threshold_var = tk.DoubleVar(value=self.settings.get("face_detection", {}).get("eye_aspect_ratio_threshold"))
        ttk.Scale(ear_threshold_frame, from_=0.1, to=0.4, orient=tk.HORIZONTAL, variable=self.ear_threshold_var).pack(fill=tk.X)

        blink_actions_frame = ttk.LabelFrame(parent, text="Blink Actions", padding="10")
        blink_actions_frame.pack(fill=tk.X, pady=5)

        self.left_blink_action_var = tk.StringVar(value=self.settings.get("face_detection", {}).get("blink_left_action"))
        ttk.Label(blink_actions_frame, text="Left Blink:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Combobox(blink_actions_frame, textvariable=self.left_blink_action_var, values=["left_click", "right_click", "double_click", "scroll_up", "scroll_down"]).grid(row=0, column=1, padx=5, pady=5)

        self.right_blink_action_var = tk.StringVar(value=self.settings.get("face_detection", {}).get("blink_right_action"))
        ttk.Label(blink_actions_frame, text="Right Blink:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Combobox(blink_actions_frame, textvariable=self.right_blink_action_var, values=["left_click", "right_click", "double_click", "scroll_up", "scroll_down"]).grid(row=1, column=1, padx=5, pady=5)

    def create_gestures_tab(self, parent):
        gestures_info = """
        Hand Gestures:
        - Mouse Movement: Move your index finger.
        - Left Click: Pinch your thumb and index finger.
        - Right Click: Pinch your thumb and middle finger.
        - Scroll: Move your hand up or down while making a fist.

        Face Gestures:
        - Mouse Movement: Move your head.
        - Left Click: Blink your left eye.
        - Right Click: Blink your right eye.
        """
        ttk.Label(parent, text=gestures_info, wraplength=450, justify=tk.LEFT).pack(pady=10, padx=10)

    def load_settings_to_gui(self):
        pass

    def save_settings(self):
        self.settings["control_mode"] = self.control_mode_var.get()
        self.settings["mouse_sensitivity"] = self.sensitivity_var.get()
        self.settings["hand_gestures"] = {"click_threshold": self.click_threshold_var.get()}
        self.settings["face_detection"] = {
            "eye_aspect_ratio_threshold": self.ear_threshold_var.get(),
            "blink_left_action": self.left_blink_action_var.get(),
            "blink_right_action": self.right_blink_action_var.get()
        }
        config_manager.save_settings(self.settings)
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")
        self.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    SettingsGUI(root).pack(expand=True, fill=tk.BOTH)
    root.mainloop()
