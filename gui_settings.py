import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import config_manager 

class SettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pengaturan AuraMouse")
        try:
            self.style = ttk.Style()
            available_themes = self.style.theme_names()
            if 'clam' in available_themes:
                self.style.theme_use('clam')
            elif 'vista' in available_themes: 
                 self.style.theme_use('vista')
        except tk.TclError:
            print("Tema ttk default digunakan.")

        self.settings = config_manager.load_settings()

        default_font = ("Segoe UI", 10) 
        self.style.configure('.', font=default_font)
        self.style.configure('TLabel', font=default_font)
        self.style.configure('TButton', font=default_font, padding=5)
        self.style.configure('TRadiobutton', font=default_font)
        self.style.configure('TCheckbutton', font=default_font)
        self.style.configure('TScale', troughrelief='flat')

        self.create_widgets()
        self.load_settings_to_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Notebook for tabs ---
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill=tk.BOTH, pady=10)

        # --- Tab: Umum & Mouse ---
        tab_general_mouse = ttk.Frame(notebook, padding="10")
        notebook.add(tab_general_mouse, text=" Umum & Mouse ")

        mode_frame = ttk.LabelFrame(tab_general_mouse, text="Mode Kontrol", padding="10")
        mode_frame.pack(fill=tk.X, pady=10)
        self.control_mode_var = tk.StringVar(value=self.settings.get("control_mode", "hand"))
        ttk.Radiobutton(mode_frame, text="Tangan", variable=self.control_mode_var, value="hand").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Kepala (Wajah)", variable=self.control_mode_var, value="face").pack(side=tk.LEFT, padx=5)

        mouse_frame = ttk.LabelFrame(tab_general_mouse, text="Pengaturan Mouse & Pointer", padding="10")
        mouse_frame.pack(fill=tk.X, pady=10)

        ttk.Label(mouse_frame, text="Sensitivitas Mouse:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sensitivity_var = tk.DoubleVar(value=self.settings.get("mouse_sensitivity", 0.3))
        self.sensitivity_scale = ttk.Scale(mouse_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, variable=self.sensitivity_var, length=200)
        self.sensitivity_scale.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.sensitivity_label = ttk.Label(mouse_frame, text=f"{self.sensitivity_var.get():.2f}")
        self.sensitivity_scale.config(command=lambda val: self.sensitivity_label.config(text=f"{float(val):.2f}"))
        self.sensitivity_label.grid(row=0, column=2, padx=5)

        ttk.Label(mouse_frame, text="Durasi Dwell Click (detik):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dwell_duration_var = tk.DoubleVar(value=self.settings.get("dwell_click_duration", 1.0))
        self.dwell_scale = ttk.Scale(mouse_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL, variable=self.dwell_duration_var, length=200)
        self.dwell_scale.grid(row=1, column=1, sticky=tk.EW, padx=5)
        self.dwell_label = ttk.Label(mouse_frame, text=f"{self.dwell_duration_var.get():.1f} s")
        self.dwell_scale.config(command=lambda val: self.dwell_label.config(text=f"{float(val):.1f} s"))
        self.dwell_label.grid(row=1, column=2, padx=5)
        
        ttk.Label(mouse_frame, text="Padding Area Aktif (%):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.padding_var = tk.DoubleVar(value=self.settings.get("active_region_padding", 0.10) * 100)
        self.padding_scale = ttk.Scale(mouse_frame, from_=0, to=30, orient=tk.HORIZONTAL, variable=self.padding_var, length=200)
        self.padding_scale.grid(row=2, column=1, sticky=tk.EW, padx=5)
        self.padding_label = ttk.Label(mouse_frame, text=f"{self.padding_var.get():.0f}%")
        self.padding_scale.config(command=lambda val: self.padding_label.config(text=f"{float(val):.0f}%"))
        self.padding_label.grid(row=2, column=2, padx=5)

        # --- Tab: Gestur Tangan ---
        tab_hand_gestures = ttk.Frame(notebook, padding="10")
        notebook.add(tab_hand_gestures, text=" Gestur Tangan ")

        hand_gesture_frame = ttk.LabelFrame(tab_hand_gestures, text="Konfigurasi Gestur Tangan", padding="10")
        hand_gesture_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(hand_gesture_frame, text="Threshold Jarak Klik (px):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.click_threshold_var = tk.IntVar(value=self.settings.get("click_gesture_threshold", 30))
        self.click_threshold_scale = ttk.Scale(hand_gesture_frame, from_=10, to=100, orient=tk.HORIZONTAL, variable=self.click_threshold_var, length=200)
        self.click_threshold_scale.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.click_threshold_label = ttk.Label(hand_gesture_frame, text=f"{self.click_threshold_var.get()} px")
        self.click_threshold_scale.config(command=lambda val: self.click_threshold_label.config(text=f"{float(val):.0f} px"))
        self.click_threshold_label.grid(row=0, column=2, padx=5)

        ttk.Label(hand_gesture_frame, text="Faktor Ketat Pinch:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pinch_factor_var = tk.DoubleVar(value=self.settings.get("pinch_strictness_factor", 1.0))
        self.pinch_factor_scale = ttk.Scale(hand_gesture_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, variable=self.pinch_factor_var, length=200)
        self.pinch_factor_scale.grid(row=1, column=1, sticky=tk.EW, padx=5)
        self.pinch_factor_label = ttk.Label(hand_gesture_frame, text=f"{self.pinch_factor_var.get():.2f}")
        self.pinch_factor_scale.config(command=lambda val: self.pinch_factor_label.config(text=f"{float(val):.2f}"))
        self.pinch_factor_label.grid(row=1, column=2, padx=5)

        ttk.Label(hand_gesture_frame, text="Offset Sens. Jempol Y (px):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.thumb_offset_var = tk.IntVar(value=self.settings.get("thumb_up_sensitivity_y_offset", 5))
        self.thumb_offset_scale = ttk.Scale(hand_gesture_frame, from_=-20, to=20, orient=tk.HORIZONTAL, variable=self.thumb_offset_var, length=200)
        self.thumb_offset_scale.grid(row=2, column=1, sticky=tk.EW, padx=5)
        self.thumb_offset_label = ttk.Label(hand_gesture_frame, text=f"{self.thumb_offset_var.get()} px")
        self.thumb_offset_scale.config(command=lambda val: self.thumb_offset_label.config(text=f"{float(val):.0f} px"))
        self.thumb_offset_label.grid(row=2, column=2, padx=5)

        ttk.Label(hand_gesture_frame, text="Offset Sens. Jari Y (px):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.finger_offset_var = tk.IntVar(value=self.settings.get("finger_up_sensitivity_y_offset", 5))
        self.finger_offset_scale = ttk.Scale(hand_gesture_frame, from_=-20, to=20, orient=tk.HORIZONTAL, variable=self.finger_offset_var, length=200)
        self.finger_offset_scale.grid(row=3, column=1, sticky=tk.EW, padx=5)
        self.finger_offset_label = ttk.Label(hand_gesture_frame, text=f"{self.finger_offset_var.get()} px")
        self.finger_offset_scale.config(command=lambda val: self.finger_offset_label.config(text=f"{float(val):.0f} px"))
        self.finger_offset_label.grid(row=3, column=2, padx=5)
        
        self.debug_log_var = tk.BooleanVar(value=self.settings.get("debug_gesture_logging", False))
        ttk.Checkbutton(hand_gesture_frame, text="Aktifkan Debug Log Gestur", variable=self.debug_log_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=10)

        # --- Tab: Keyboard Virtual ---
        tab_keyboard = ttk.Frame(notebook, padding="10")
        notebook.add(tab_keyboard, text=" Keyboard Virtual ")

        kb_frame = ttk.LabelFrame(tab_keyboard, text="Pengaturan Keyboard Virtual", padding="10")
        kb_frame.pack(fill=tk.X, pady=10)

        ttk.Label(kb_frame, text="Tampilkan saat startup:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.kb_show_startup_var = tk.BooleanVar(value=self.settings.get("keyboard_show_on_startup", False))
        ttk.Checkbutton(kb_frame, variable=self.kb_show_startup_var).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(kb_frame, text="Layout:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.kb_layout_var = tk.StringVar(value=self.settings.get("keyboard_layout", "qwerty_id"))
        # Add more layouts as they are implemented in VirtualKeyboard
        kb_layouts = ["qwerty_id", "qwerty_en"] 
        ttk.Combobox(kb_frame, textvariable=self.kb_layout_var, values=kb_layouts, state="readonly").grid(row=1, column=1, sticky=tk.EW)

        ttk.Label(kb_frame, text="Tema:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.kb_theme_var = tk.StringVar(value=self.settings.get("keyboard_theme", "light"))
        kb_themes = ["light", "dark"] # Add "custom" if implemented
        ttk.Combobox(kb_frame, textvariable=self.kb_theme_var, values=kb_themes, state="readonly").grid(row=2, column=1, sticky=tk.EW)

        ttk.Label(kb_frame, text="Dwell Time Tombol (detik):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.kb_dwell_var = tk.DoubleVar(value=self.settings.get("keyboard_dwell_time", 0.7))
        self.kb_dwell_scale = ttk.Scale(kb_frame, from_=0.3, to=2.0, orient=tk.HORIZONTAL, variable=self.kb_dwell_var, length=150)
        self.kb_dwell_scale.grid(row=3, column=1, sticky=tk.EW, padx=5)
        self.kb_dwell_label = ttk.Label(kb_frame, text=f"{self.kb_dwell_var.get():.1f} s")
        self.kb_dwell_scale.config(command=lambda val: self.kb_dwell_label.config(text=f"{float(val):.1f} s"))
        self.kb_dwell_label.grid(row=3, column=2, padx=5)

        ttk.Label(kb_frame, text="Tombol Toggle Fisik:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.kb_toggle_key_var = tk.StringVar(value=self.settings.get("keyboard_toggle_key", "k"))
        ttk.Entry(kb_frame, textvariable=self.kb_toggle_key_var, width=5).grid(row=4, column=1, sticky=tk.W)
        # Add more keyboard settings as needed (e.g., key_sound_enabled)

        # --- Tombol Aksi ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=20, side=tk.BOTTOM)

        self.save_button = ttk.Button(action_frame, text="Simpan Pengaturan", command=self.save_gui_settings)
        self.save_button.pack(side=tk.LEFT, padx=10, expand=True)

        self.reset_button = ttk.Button(action_frame, text="Reset ke Default", command=self.confirm_reset_settings)
        self.reset_button.pack(side=tk.LEFT, padx=10, expand=True)

        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack(pady=5, side=tk.BOTTOM)
        
    def update_labels_from_vars(self):
        self.sensitivity_label.config(text=f"{self.sensitivity_var.get():.2f}")
        self.dwell_label.config(text=f"{self.dwell_duration_var.get():.1f} s")
        self.padding_label.config(text=f"{self.padding_var.get():.0f}%")
        self.click_threshold_label.config(text=f"{self.click_threshold_var.get()} px")
        self.pinch_factor_label.config(text=f"{self.pinch_factor_var.get():.2f}")
        self.thumb_offset_label.config(text=f"{self.thumb_offset_var.get()} px")
        self.finger_offset_label.config(text=f"{self.finger_offset_var.get()} px")
        self.kb_dwell_label.config(text=f"{self.kb_dwell_var.get():.1f} s")


    def load_settings_to_gui(self):
        self.control_mode_var.set(self.settings.get("control_mode", "hand"))
        self.sensitivity_var.set(self.settings.get("mouse_sensitivity", 0.3))
        self.dwell_duration_var.set(self.settings.get("dwell_click_duration", 1.0))
        self.padding_var.set(self.settings.get("active_region_padding", 0.10) * 100)
        
        self.click_threshold_var.set(self.settings.get("click_gesture_threshold", 30))
        self.pinch_factor_var.set(self.settings.get("pinch_strictness_factor", 1.0))
        self.thumb_offset_var.set(self.settings.get("thumb_up_sensitivity_y_offset", 5))
        self.finger_offset_var.set(self.settings.get("finger_up_sensitivity_y_offset", 5))
        self.debug_log_var.set(self.settings.get("debug_gesture_logging", False))

        self.kb_show_startup_var.set(self.settings.get("keyboard_show_on_startup", False))
        self.kb_layout_var.set(self.settings.get("keyboard_layout", "qwerty_id"))
        self.kb_theme_var.set(self.settings.get("keyboard_theme", "light"))
        self.kb_dwell_var.set(self.settings.get("keyboard_dwell_time", 0.7))
        self.kb_toggle_key_var.set(self.settings.get("keyboard_toggle_key", "k"))

        self.update_labels_from_vars()
        self.status_label.config(text="Pengaturan dimuat.", foreground="green")


    def save_gui_settings(self):
        self.settings["control_mode"] = self.control_mode_var.get()
        self.settings["mouse_sensitivity"] = round(self.sensitivity_var.get(), 2)
        self.settings["dwell_click_duration"] = round(self.dwell_duration_var.get(), 1)
        self.settings["active_region_padding"] = round(self.padding_var.get() / 100, 2)
        
        self.settings["click_gesture_threshold"] = int(self.click_threshold_var.get())
        self.settings["pinch_strictness_factor"] = round(self.pinch_factor_var.get(), 2)
        self.settings["thumb_up_sensitivity_y_offset"] = int(self.thumb_offset_var.get())
        self.settings["finger_up_sensitivity_y_offset"] = int(self.finger_offset_var.get())
        self.settings["debug_gesture_logging"] = self.debug_log_var.get()

        self.settings["keyboard_show_on_startup"] = self.kb_show_startup_var.get()
        self.settings["keyboard_layout"] = self.kb_layout_var.get()
        self.settings["keyboard_theme"] = self.kb_theme_var.get()
        self.settings["keyboard_dwell_time"] = round(self.kb_dwell_var.get(), 1)
        self.settings["keyboard_toggle_key"] = self.kb_toggle_key_var.get()
        
        if config_manager.save_settings(self.settings):
            self.status_label.config(text="Pengaturan berhasil disimpan!", foreground="green")
            messagebox.showinfo("Sukses", "Pengaturan berhasil disimpan.")
        else:
            self.status_label.config(text="Gagal menyimpan pengaturan.", foreground="red")
            messagebox.showerror("Error", "Gagal menyimpan pengaturan.")

    def confirm_load_settings(self): 
        if messagebox.askokcancel("Muat Pengaturan", "Ini akan menimpa perubahan yang belum disimpan. Lanjutkan?"):
            self.settings = config_manager.load_settings()
            self.load_settings_to_gui()

    def confirm_reset_settings(self):
        if messagebox.askyesno("Reset Pengaturan", "Anda yakin ingin mengembalikan semua pengaturan ke default?"):
            self.settings = config_manager.DEFAULT_SETTINGS.copy() 
            config_manager.save_settings(self.settings) 
            self.load_settings_to_gui()
            self.status_label.config(text="Pengaturan direset ke default.", foreground="blue")

    def on_closing(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsGUI(root)
    root.mainloop()