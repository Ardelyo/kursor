import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import config_manager # Impor modul config_manager kita

class SettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pengaturan AuraMouse")
        # Coba set tema yang lebih modern jika tersedia (misalnya 'clam', 'alt', 'default', 'classic')
        try:
            self.style = ttk.Style()
            # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
            available_themes = self.style.theme_names()
            # print("Available themes:", available_themes)
            if 'clam' in available_themes:
                self.style.theme_use('clam')
            elif 'vista' in available_themes: # Untuk tampilan Windows yang lebih baik
                 self.style.theme_use('vista')
        except tk.TclError:
            print("Tema ttk default digunakan.")


        self.settings = config_manager.load_settings()

        # Atur ukuran font default yang lebih besar
        default_font = ("Segoe UI", 10) # Atau "Arial", "Calibri"
        self.style.configure('.', font=default_font)
        self.style.configure('TLabel', font=default_font)
        self.style.configure('TButton', font=default_font, padding=5)
        self.style.configure('TRadiobutton', font=default_font)
        self.style.configure('TCheckbutton', font=default_font)
        self.style.configure('TScale', troughrelief='flat')


        self.create_widgets()
        self.load_settings_to_gui()

        # Menangani penutupan jendela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Pilihan Mode ---
        mode_frame = ttk.LabelFrame(main_frame, text="Mode Kontrol", padding="10")
        mode_frame.pack(fill=tk.X, pady=10)

        self.control_mode_var = tk.StringVar(value=self.settings.get("control_mode", "hand"))
        ttk.Radiobutton(mode_frame, text="Tangan", variable=self.control_mode_var, value="hand").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Kepala (Wajah)", variable=self.control_mode_var, value="face").pack(side=tk.LEFT, padx=5)

        # --- Pengaturan Mouse ---
        mouse_frame = ttk.LabelFrame(main_frame, text="Pengaturan Mouse & Pointer", padding="10")
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
        self.padding_var = tk.DoubleVar(value=self.settings.get("active_region_padding", 0.10) * 100) # Simpan sebagai 0-1, tampilkan 0-100
        self.padding_scale = ttk.Scale(mouse_frame, from_=0, to=30, orient=tk.HORIZONTAL, variable=self.padding_var, length=200) # 0% to 30%
        self.padding_scale.grid(row=2, column=1, sticky=tk.EW, padx=5)
        self.padding_label = ttk.Label(mouse_frame, text=f"{self.padding_var.get():.0f}%")
        self.padding_scale.config(command=lambda val: self.padding_label.config(text=f"{float(val):.0f}%"))
        self.padding_label.grid(row=2, column=2, padx=5)

        # --- Pengaturan Gestur (Contoh sederhana) ---
        gesture_frame = ttk.LabelFrame(main_frame, text="Pengaturan Gestur Tangan", padding="10")
        gesture_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(gesture_frame, text="Threshold Jarak Klik (px):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.click_threshold_var = tk.IntVar(value=self.settings.get("click_gesture_threshold", 30))
        self.click_threshold_scale = ttk.Scale(gesture_frame, from_=10, to=100, orient=tk.HORIZONTAL, variable=self.click_threshold_var, length=200)
        self.click_threshold_scale.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.click_threshold_label = ttk.Label(gesture_frame, text=f"{self.click_threshold_var.get()} px")
        self.click_threshold_scale.config(command=lambda val: self.click_threshold_label.config(text=f"{float(val):.0f} px")) # float(val) agar bisa menampilkan nilai saat digeser
        self.click_threshold_label.grid(row=0, column=2, padx=5)


        # --- Tombol Aksi ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=20)

        self.save_button = ttk.Button(action_frame, text="Simpan Pengaturan", command=self.save_gui_settings)
        self.save_button.pack(side=tk.LEFT, padx=10, expand=True)

        self.load_button = ttk.Button(action_frame, text="Muat Pengaturan", command=self.confirm_load_settings) # Jarang dipakai jika auto-load
        # self.load_button.pack(side=tk.LEFT, padx=10, expand=True) # Opsional

        self.reset_button = ttk.Button(action_frame, text="Reset ke Default", command=self.confirm_reset_settings)
        self.reset_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Placeholder untuk informasi status
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack(pady=5)
        
        # Kolom kiri dan kanan untuk pengaturan yang lebih banyak
        # content_frame = ttk.Frame(main_frame)
        # content_frame.pack(fill=tk.BOTH, expand=True)
        # left_column = ttk.Frame(content_frame, padding="10")
        # left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # right_column = ttk.Frame(content_frame, padding="10")
        # right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Pindahkan frame-frame di atas ke left_column atau right_column


    def update_labels_from_vars(self):
        """Panggil ini untuk memastikan label numerik di sebelah slider diperbarui."""
        self.sensitivity_label.config(text=f"{self.sensitivity_var.get():.2f}")
        self.dwell_label.config(text=f"{self.dwell_duration_var.get():.1f} s")
        self.padding_label.config(text=f"{self.padding_var.get():.0f}%")
        self.click_threshold_label.config(text=f"{self.click_threshold_var.get()} px")

    def load_settings_to_gui(self):
        """Memuat nilai dari dictionary self.settings ke elemen GUI."""
        self.control_mode_var.set(self.settings.get("control_mode", "hand"))
        self.sensitivity_var.set(self.settings.get("mouse_sensitivity", 0.3))
        self.dwell_duration_var.set(self.settings.get("dwell_click_duration", 1.0))
        self.padding_var.set(self.settings.get("active_region_padding", 0.10) * 100)
        self.click_threshold_var.set(self.settings.get("click_gesture_threshold", 30))
        self.update_labels_from_vars()
        self.status_label.config(text="Pengaturan dimuat.", foreground="green")


    def save_gui_settings(self):
        """Mengambil nilai dari GUI dan menyimpannya ke self.settings lalu ke file."""
        self.settings["control_mode"] = self.control_mode_var.get()
        self.settings["mouse_sensitivity"] = round(self.sensitivity_var.get(), 2)
        self.settings["dwell_click_duration"] = round(self.dwell_duration_var.get(), 1)
        self.settings["active_region_padding"] = round(self.padding_var.get() / 100, 2) # Simpan sebagai 0-1
        self.settings["click_gesture_threshold"] = int(self.click_threshold_var.get())
        
        if config_manager.save_settings(self.settings):
            self.status_label.config(text="Pengaturan berhasil disimpan!", foreground="green")
            messagebox.showinfo("Sukses", "Pengaturan berhasil disimpan.")
            # Di sini Anda mungkin ingin memberi sinyal ke main.py bahwa pengaturan telah berubah
        else:
            self.status_label.config(text="Gagal menyimpan pengaturan.", foreground="red")
            messagebox.showerror("Error", "Gagal menyimpan pengaturan.")

    def confirm_load_settings(self): # Biasanya tidak perlu jika auto-load saat start
        if messagebox.askokcancel("Muat Pengaturan", "Ini akan menimpa perubahan yang belum disimpan. Lanjutkan?"):
            self.settings = config_manager.load_settings()
            self.load_settings_to_gui()

    def confirm_reset_settings(self):
        if messagebox.askyesno("Reset Pengaturan", "Anda yakin ingin mengembalikan semua pengaturan ke default?"):
            self.settings = config_manager.DEFAULT_SETTINGS.copy() # Ambil salinan bersih
            config_manager.save_settings(self.settings) # Simpan default baru ke file
            self.load_settings_to_gui()
            self.status_label.config(text="Pengaturan direset ke default.", foreground="blue")

    def on_closing(self):
        # Anda bisa menambahkan logika untuk mengecek perubahan yang belum disimpan di sini
        # if self.has_unsaved_changes():
        #     if messagebox.askokcancel("Keluar", "Ada perubahan yang belum disimpan. Tetap keluar?"):
        #         self.root.destroy()
        # else:
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsGUI(root)
    root.mainloop()