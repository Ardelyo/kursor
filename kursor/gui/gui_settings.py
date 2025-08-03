
import tkinter as tk
from tkinter import ttk, messagebox
from kursor.config import config_manager

class SettingsGUI(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, padding="10", **kwargs)

        self.settings = config_manager.load_settings()

        self.create_widgets()
        self.load_settings_to_gui()

    def create_widgets(self):
        # Use a notebook for tabbed layout
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill=tk.BOTH)

        # General Tab
        general_tab = ttk.Frame(notebook, padding="10")
        notebook.add(general_tab, text="General")
        self.create_general_tab(general_tab)

        # Hand Tab
        hand_tab = ttk.Frame(notebook, padding="10")
        notebook.add(hand_tab, text="Hand Tracking")
        self.create_hand_tab(hand_tab)

        # Face Tab
        face_tab = ttk.Frame(notebook, padding="10")
        notebook.add(face_tab, text="Face Tracking")
        self.create_face_tab(face_tab)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings)
        save_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.master.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def create_general_tab(self, parent):
        # Control Mode
        mode_frame = ttk.LabelFrame(parent, text="Control Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=5)
        self.control_mode_var = tk.StringVar(value=self.settings.get("control_mode"))
        ttk.Radiobutton(mode_frame, text="Hand", variable=self.control_mode_var, value="hand").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Face", variable=self.control_mode_var, value="face").pack(side=tk.LEFT, padx=5)

        # Mouse Sensitivity
        sensitivity_frame = ttk.LabelFrame(parent, text="Mouse Sensitivity", padding="10")
        sensitivity_frame.pack(fill=tk.X, pady=5)
        self.sensitivity_var = tk.DoubleVar(value=self.settings.get("mouse_sensitivity"))
        ttk.Scale(sensitivity_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, variable=self.sensitivity_var).pack(fill=tk.X)

    def create_hand_tab(self, parent):
        # Hand settings here
        ttk.Label(parent, text="Hand tracking settings will go here.").pack()

    def create_face_tab(self, parent):
        # Face settings here
        ttk.Label(parent, text="Face tracking settings will go here.").pack()

    def load_settings_to_gui(self):
        # This will be expanded to load all settings
        pass

    def save_settings(self):
        self.settings["control_mode"] = self.control_mode_var.get()
        self.settings["mouse_sensitivity"] = self.sensitivity_var.get()
        config_manager.save_settings(self.settings)
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    SettingsGUI(root).pack(expand=True, fill=tk.BOTH)
    root.mainloop()
