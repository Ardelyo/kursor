
import time
import cv2
import numpy as np
import pyautogui # Akan digunakan nanti untuk mengetik

# Konstanta untuk ukuran dan padding keyboard bisa disesuaikan
KEY_HEIGHT = 50
KEY_WIDTH = 50 # Lebar default, bisa bervariasi untuk spasi, enter, dll.
KEY_PADDING = 5
KEYBOARD_PADDING_X = 10
KEYBOARD_PADDING_Y = 10
FONT_SCALE_FACTOR = 0.6 # Relatif terhadap KEY_HEIGHT
FONT_THICKNESS = 1

class VirtualKeyboard:
    def __init__(self, screen_width, screen_height, 
                 layout_name="qwerty_id", theme_name="light", 
                 key_sound_enabled=False, dwell_time=0.7):
        
        self.screen_width = screen_width # Resolusi layar monitor
        self.screen_height = screen_height # Resolusi layar monitor

        self.layout_name = layout_name
        self.theme_name = theme_name
        self.key_sound_enabled = key_sound_enabled # Belum diimplementasikan
        self.dwell_time = dwell_time # Belum diimplementasikan untuk aksi

        self.keys_config = [] # List of dictionaries, each defining a key
        self.colors = {}
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        self.is_visible = False
        self.shift_active = False
        self.caps_lock_active = False
        self.alt_gr_active = False # Untuk beberapa layout

        self.hovered_key_index = -1 # Indeks kunci yang sedang di-hover
        self.dwell_on_key_start_time = 0
        self.dwell_key_triggered = False

        self._load_theme()
        self._generate_layout() # Panggil ini untuk membuat layout awal

        # Hitung dimensi total keyboard berdasarkan layout yang dihasilkan
        self.keyboard_width_px, self.keyboard_height_px = self._calculate_keyboard_dimensions()
        # Posisi keyboard (misalnya, tengah bawah frame kamera)
        # Ini akan dihitung ulang di draw() relatif terhadap frame kamera
        self.keyboard_pos_x = 0 
        self.keyboard_pos_y = 0


    def _load_theme(self):
        if self.theme_name == "dark":
            self.colors = {
                "bg": (50, 50, 50),
                "key_normal_bg": (80, 80, 80),
                "key_normal_text": (220, 220, 220),
                "key_hover_bg": (120, 120, 120),
                "key_hover_text": (255, 255, 255),
                "key_pressed_bg": (150, 150, 150), # Belum dipakai
                "key_pressed_text": (255, 255, 255), # Belum dipakai
                "key_special_bg": (60, 60, 60),
                "key_special_text": (200, 200, 200),
            }
        else: # Default to light theme
            self.colors = {
                "bg": (220, 220, 220),
                "key_normal_bg": (255, 255, 255),
                "key_normal_text": (30, 30, 30),
                "key_hover_bg": (200, 210, 230),
                "key_hover_text": (0, 0, 0),
                "key_pressed_bg": (180, 190, 210),
                "key_pressed_text": (0, 0, 0),
                "key_special_bg": (200, 200, 200),
                "key_special_text": (50, 50, 50),
            }

    def _generate_key(self, char, shifted_char=None, alt_char=None, 
                      key_type="char", width_multiplier=1, 
                      display_text=None, action=None):
        """Helper untuk membuat dictionary konfigurasi kunci."""
        return {
            "char": char,
            "shifted_char": shifted_char if shifted_char is not None else char.upper() if char else None,
            "alt_char": alt_char, # Untuk AltGr
            "display_text": display_text if display_text is not None else char, # Teks yang ditampilkan di tombol
            "key_type": key_type, # 'char', 'shift', 'caps', 'bksp', 'enter', 'space', 'tab', 'altgr', 'mode'
            "width_px": int(KEY_WIDTH * width_multiplier),
            "height_px": KEY_HEIGHT,
            "action": action if action is not None else char, # Aksi yang dilakukan (misal, 'backspace')
            # 'rect' dan 'pos' akan dihitung nanti
        }

    def _generate_layout(self):
        """Membuat layout tombol berdasarkan self.layout_name."""
        self.keys_config = [] # Reset konfigurasi kunci

        if self.layout_name == "qwerty_id" or self.layout_name == "qwerty_en":
            # Definisi baris-baris tombol (char, shifted_char, alt_char, type, width_mult, display_override, action_override)
            rows_data = [
                [ # Baris 1 (angka dan simbol)
                    ('`', '~', None, "char", 1, None, None), ('1', '!', None, "char", 1, None, None), 
                    ('2', '@', None, "char", 1, None, None), ('3', '#', None, "char", 1, None, None),
                    ('4', '$', None, "char", 1, None, None), ('5', '%', None, "char", 1, None, None), 
                    ('6', '^', None, "char", 1, None, None), ('7', '&', None, "char", 1, None, None),
                    ('8', '*', None, "char", 1, None, None), ('9', '(', None, "char", 1, None, None), 
                    ('0', ')', None, "char", 1, None, None), ('-', '_', None, "char", 1, None, None),
                    ('=', '+', None, "char", 1, None, None), 
                    (None, None, None, "bksp", 2, "Bksp", "backspace")
                ],
                [ # Baris 2 (QWERTY)
                    (None, None, None, "tab", 1.5, "Tab", "tab"),
                    ('q', 'Q', None, "char", 1), ('w', 'W', None, "char", 1), ('e', 'E', None, "char", 1),
                    ('r', 'R', None, "char", 1), ('t', 'T', None, "char", 1), ('y', 'Y', None, "char", 1),
                    ('u', 'U', None, "char", 1), ('i', 'I', None, "char", 1), ('o', 'O', None, "char", 1),
                    ('p', 'P', None, "char", 1), ('[', '{', None, "char", 1), (']', '}', None, "char", 1),
                    ('\\', '|', None, "char", 1.5)
                ],
                [ # Baris 3 (ASDFGH)
                    (None, None, None, "caps", 1.8, "Caps", "caps_lock"),
                    ('a', 'A', None, "char", 1), ('s', 'S', None, "char", 1), ('d', 'D', None, "char", 1),
                    ('f', 'F', None, "char", 1), ('g', 'G', None, "char", 1), ('h', 'H', None, "char", 1),
                    ('j', 'J', None, "char", 1), ('k', 'K', None, "char", 1), ('l', 'L', None, "char", 1),
                    (';', ':', None, "char", 1), ("'", '"', None, "char", 1),
                    (None, None, None, "enter", 2.2, "Enter", "enter")
                ],
                [ # Baris 4 (ZXCVBN)
                    (None, None, None, "shift", 2.5, "Shift", "shift"),
                    ('z', 'Z', None, "char", 1), ('x', 'X', None, "char", 1), ('c', 'C', None, "char", 1),
                    ('v', 'V', None, "char", 1), ('b', 'B', None, "char", 1), ('n', 'N', None, "char", 1),
                    ('m', 'M', None, "char", 1), (',', '<', None, "char", 1), ('.', '>', None, "char", 1),
                    ('/', '?', None, "char", 1),
                    (None, None, None, "shift_r", 2.5, "Shift", "shift") # Shift kanan
                ],
                [ # Baris 5 (Kontrol dan Spasi)
                    # (None, None, None, "ctrl_l", 1.5, "Ctrl", "control_l"), # Opsional
                    # (None, None, None, "win_l", 1.2, "Win", "win_l"),     # Opsional
                    # (None, None, None, "alt_l", 1.2, "Alt", "alt_l"),      # Opsional
                    (None, None, None, "space", 9, "", "space"), # Spasi lebar
                    # (None, None, None, "alt_r", 1.2, "AltGr", "alt_gr"),  # Opsional, untuk AltGr
                    # (None, None, None, "mode", 1.5, "123", "mode_numeric"), # Opsional
                    # (None, None, None, "ctrl_r", 1.5, "Ctrl", "control_r") # Opsional
                ]
            ]
        else: # Fallback ke layout QWERTY jika tidak dikenal
             print(f"Peringatan: Layout keyboard '{self.layout_name}' tidak dikenal, menggunakan QWERTY default.")
             self.layout_name = "qwerty_en" # atau "qwerty_id"
             return self._generate_layout() # Rekursi untuk memuat layout default

        # Hitung posisi dan rect untuk setiap tombol
        current_y = KEYBOARD_PADDING_Y
        for row_idx, row_data in enumerate(rows_data):
            current_x = KEYBOARD_PADDING_X
            for key_def in row_data:
                k_char, k_shift, k_alt, k_type, k_width_mult, k_display, k_action = key_def + (None,) * (7 - len(key_def)) # Padding agar bisa unpacking
                if k_char is None and k_type == "char": continue # Skip jika char kosong tapi tipe char

                key_entry = self._generate_key(
                    k_char, k_shift, k_alt, k_type, k_width_mult, k_display, k_action
                )
                key_entry["pos_x"] = current_x
                key_entry["pos_y"] = current_y
                key_entry["rect"] = (current_x, current_y, key_entry["width_px"], key_entry["height_px"])
                self.keys_config.append(key_entry)
                current_x += key_entry["width_px"] + KEY_PADDING
            current_y += KEY_HEIGHT + KEY_PADDING
        
    def _calculate_keyboard_dimensions(self):
        """Menghitung lebar dan tinggi total keyboard berdasarkan self.keys_config."""
        if not self.keys_config:
            return 0, 0
        
        max_x_coord = 0
        max_y_coord = 0
        
        for key in self.keys_config:
            # key['rect'] adalah (x, y, w, h) relatif terhadap pojok kiri atas keyboard
            key_right_edge = key["pos_x"] + key["width_px"]
            key_bottom_edge = key["pos_y"] + key["height_px"]
            if key_right_edge > max_x_coord:
                max_x_coord = key_right_edge
            if key_bottom_edge > max_y_coord:
                max_y_coord = key_bottom_edge
                
        total_width = max_x_coord + KEYBOARD_PADDING_X # Tambah padding kanan
        total_height = max_y_coord + KEYBOARD_PADDING_Y # Tambah padding bawah
        return int(total_width), int(total_height)

    def set_visibility(self, visible):
        self.is_visible = visible
        if not visible:
            self.hovered_key_index = -1 # Reset hover saat disembunyikan
            self.dwell_on_key_start_time = 0
            self.dwell_key_triggered = False

    def _get_display_char_for_key(self, key_config):
        """Mendapatkan karakter yang akan ditampilkan pada tombol berdasarkan state."""
        char_to_display = key_config["display_text"] # Default ke display_text (misal "Bksp", "Shift")

        if key_config["key_type"] == "char":
            if self.alt_gr_active and key_config["alt_char"]:
                char_to_display = key_config["alt_char"]
            elif self.shift_active or self.caps_lock_active:
                # Untuk CAPS LOCK, hanya huruf yang jadi kapital. Shift mempengaruhi semua.
                if self.caps_lock_active and key_config["char"] and key_config["char"].isalpha():
                    char_to_display = key_config["char"].upper()
                    # Jika shift juga aktif, gunakan shifted_char (misal untuk angka+simbol)
                    if self.shift_active and key_config["shifted_char"]:
                         char_to_display = key_config["shifted_char"]
                elif self.shift_active and key_config["shifted_char"]:
                    char_to_display = key_config["shifted_char"]
                else: # Default jika hanya char biasa atau caps lock non-alpha
                    char_to_display = key_config["char"]
            else: # Normal
                char_to_display = key_config["char"]
        return str(char_to_display) if char_to_display is not None else ""


    def draw(self, frame, pointer_x_cam_abs, pointer_y_cam_abs):
        """
        Menggambar keyboard ke frame.
        pointer_x_cam_abs, pointer_y_cam_abs: Koordinat pointer absolut di frame kamera.
        """
        if not self.is_visible:
            return frame

        cam_h, cam_w, _ = frame.shape

        # Posisi keyboard: tengah bawah frame kamera
        self.keyboard_pos_x = (cam_w - self.keyboard_width_px) // 2
        self.keyboard_pos_y = cam_h - self.keyboard_height_px - 20 # 20px dari bawah

        # Buat overlay untuk keyboard agar bisa transparan (opsional)
        overlay = frame.copy()
        
        # Gambar background keyboard
        cv2.rectangle(overlay, 
                      (self.keyboard_pos_x, self.keyboard_pos_y), 
                      (self.keyboard_pos_x + self.keyboard_width_px, self.keyboard_pos_y + self.keyboard_height_px), 
                      self.colors["bg"], -1)

        self.hovered_key_index = -1 # Reset sebelum cek hover baru

        for idx, key in enumerate(self.keys_config):
            # Koordinat tombol absolut di frame kamera
            abs_key_x = self.keyboard_pos_x + key["pos_x"]
            abs_key_y = self.keyboard_pos_y + key["pos_y"]
            abs_key_w = key["width_px"]
            abs_key_h = key["height_px"]

            is_hovered = False
            if abs_key_x < pointer_x_cam_abs < abs_key_x + abs_key_w and \
               abs_key_y < pointer_y_cam_abs < abs_key_y + abs_key_h:
                is_hovered = True
                self.hovered_key_index = idx

            key_bg_color = self.colors["key_normal_bg"]
            key_text_color = self.colors["key_normal_text"]

            if key["key_type"] not in ["char", "space"]: # Tombol spesial
                key_bg_color = self.colors.get("key_special_bg", key_bg_color)
                key_text_color = self.colors.get("key_special_text", key_text_color)
            
            # Highlight untuk Shift/Caps aktif
            if (key["key_type"] == "shift" and self.shift_active) or \
               (key["key_type"] == "caps" and self.caps_lock_active) or \
               (key["key_type"] == "alt_gr" and self.alt_gr_active):
                key_bg_color = self.colors["key_pressed_bg"] # Gunakan warna pressed untuk indikasi aktif
            
            if is_hovered:
                key_bg_color = self.colors["key_hover_bg"]
                key_text_color = self.colors["key_hover_text"]
            
            cv2.rectangle(overlay, (abs_key_x, abs_key_y), 
                          (abs_key_x + abs_key_w, abs_key_y + abs_key_h), 
                          key_bg_color, -1)
            # Border tombol
            cv2.rectangle(overlay, (abs_key_x, abs_key_y), 
                          (abs_key_x + abs_key_w, abs_key_y + abs_key_h), 
                          self.colors["key_normal_text"], 1) 

            char_to_display = self._get_display_char_for_key(key)
            
            # Hitung ukuran teks untuk penempatan tengah
            font_dynamic_scale = (KEY_HEIGHT / 70.0) * FONT_SCALE_FACTOR # Skala font dinamis
            (text_w, text_h), baseline = cv2.getTextSize(char_to_display, self.font, font_dynamic_scale, FONT_THICKNESS)
            
            text_x = abs_key_x + (abs_key_w - text_w) // 2
            text_y = abs_key_y + (abs_key_h + text_h) // 2 - baseline // 2 # Penyesuaian baseline

            cv2.putText(overlay, char_to_display, (text_x, text_y), 
                        self.font, font_dynamic_scale, key_text_color, FONT_THICKNESS, cv2.LINE_AA)

            # Dwell progress visualization (placeholder)
            if is_hovered and self.dwell_on_key_start_time > 0 and not self.dwell_key_triggered:
                elapsed_dwell = time.time() - self.dwell_on_key_start_time
                progress_ratio = min(elapsed_dwell / self.dwell_time, 1.0)
                if progress_ratio > 0:
                    cv2.rectangle(overlay,
                                  (abs_key_x, abs_key_y + abs_key_h - 5), # Bar di bawah tombol
                                  (abs_key_x + int(abs_key_w * progress_ratio), abs_key_y + abs_key_h),
                                  (0, 255, 0), -1) # Hijau untuk progres


        # Gabungkan overlay dengan frame asli (bisa dengan bobot alpha)
        alpha = 0.9 # Transparansi keyboard
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame

    def handle_input(self, pointer_x_cam_abs, pointer_y_cam_abs, click_event_from_main):
        """
        Menangani input ke keyboard (hover, dwell, klik).
        click_event_from_main: Boolean, True jika ada event klik dari main.py (gestur tangan/wajah).
        Mengembalikan karakter/aksi yang ditekan, atau None.
        """
        if not self.is_visible:
            return None

        # Ubah pointer_x_cam_abs dan pointer_y_cam_abs menjadi relatif ke keyboard
        # pointer_x_kb_rel = pointer_x_cam_abs - self.keyboard_pos_x
        # pointer_y_kb_rel = pointer_y_cam_abs - self.keyboard_pos_y
        
        # Logika hover sudah ditangani di draw() untuk mengisi self.hovered_key_index
        
        action_to_perform = None

        if self.hovered_key_index != -1:
            hovered_key_data = self.keys_config[self.hovered_key_index]
            
            # Logika Dwell Click pada Tombol
            if self.dwell_on_key_start_time == 0: # Baru mulai hover di tombol ini
                self.dwell_on_key_start_time = time.time()
                self.dwell_key_triggered = False
            else: # Sudah hover sebelumnya
                if not self.dwell_key_triggered and (time.time() - self.dwell_on_key_start_time >= self.dwell_time):
                    action_to_perform = hovered_key_data["action"]
                    self.dwell_key_triggered = True # Tandai sudah di-trigger oleh dwell
                    print(f"Keyboard Dwell: {action_to_perform}")
            
            # Logika Klik Langsung (jika ada event dari main.py dan belum di-trigger dwell)
            if click_event_from_main and not self.dwell_key_triggered:
                action_to_perform = hovered_key_data["action"]
                print(f"Keyboard Click: {action_to_perform}")
                # Reset dwell jika klik terjadi, agar tidak ada double action
                self.dwell_on_key_start_time = 0 
                self.dwell_key_triggered = False

        else: # Tidak ada tombol yang di-hover
            self.dwell_on_key_start_time = 0 # Reset timer dwell
            self.dwell_key_triggered = False


        # Jika ada aksi yang akan dilakukan
        if action_to_perform:
            # Reset state dwell untuk tombol berikutnya
            self.dwell_on_key_start_time = 0 
            self.dwell_key_triggered = False # Reset setelah aksi

            key_type = self.keys_config[self.hovered_key_index]["key_type"]
            char_to_type = ""

            if key_type == "char":
                # Tentukan karakter yang akan diketik berdasarkan Shift/Caps/AltGr
                key_conf = self.keys_config[self.hovered_key_index]
                if self.alt_gr_active and key_conf["alt_char"]:
                    char_to_type = key_conf["alt_char"]
                elif self.shift_active or self.caps_lock_active:
                    if self.caps_lock_active and key_conf["char"] and key_conf["char"].isalpha():
                        char_to_type = key_conf["char"].upper()
                        if self.shift_active and key_conf["shifted_char"]: # Shift + Caps (untuk simbol di atas angka)
                            char_to_type = key_conf["shifted_char"]
                    elif self.shift_active and key_conf["shifted_char"]:
                        char_to_type = key_conf["shifted_char"]
                    else:
                        char_to_type = key_conf["char"] # Capslock untuk non-alpha, atau shift non-aktif
                else:
                    char_to_type = key_conf["char"]
                
                if char_to_type:
                    pyautogui.typewrite(char_to_type, interval=0) # interval 0 agar cepat
                
                # Nonaktifkan shift setelah mengetik karakter (perilaku umum keyboard)
                if self.shift_active:
                    self.shift_active = False
                return char_to_type # Kembalikan karakter yang diketik

            elif action_to_perform == "shift":
                self.shift_active = not self.shift_active
                return "Shift"
            elif action_to_perform == "caps_lock":
                self.caps_lock_active = not self.caps_lock_active
                return "Caps Lock"
            elif action_to_perform == "backspace":
                pyautogui.press("backspace")
                return "Bksp"
            elif action_to_perform == "enter":
                pyautogui.press("enter")
                return "Enter"
            elif action_to_perform == "space":
                pyautogui.press("space")
                return "Space"
            elif action_to_perform == "tab":
                pyautogui.press("tab")
                return "Tab"
            # Tambahkan handler untuk alt_gr, mode, dll. jika ada
            else:
                print(f"Aksi keyboard tidak dikenal: {action_to_perform}")
                return None # Aksi tidak menghasilkan output karakter
        
        return None # Tidak ada aksi yang dilakukan atau tidak ada output karakter

if __name__ == '__main__':
    # Contoh penggunaan sederhana untuk pengujian (membutuhkan layar dummy atau capture)
    # Inisialisasi webcam dummy atau gunakan gambar statis untuk pengujian
    cam_w, cam_h = 640, 480
    dummy_frame = np.zeros((cam_h, cam_w, 3), dtype=np.uint8)

    # Inisialisasi keyboard (resolusi layar dummy untuk pengujian)
    keyboard = VirtualKeyboard(screen_width=1920, screen_height=1080, layout_name="qwerty_id", theme_name="light")
    keyboard.set_visibility(True)

    # Loop dummy untuk simulasi
    # Simulasikan posisi pointer mouse (relatif ke frame kamera)
    mock_pointer_x_cam = cam_w // 2 
    mock_pointer_y_cam = cam_h // 2 
    
    # Untuk menggerakkan pointer dummy:
    # cv2.namedWindow("Virtual Keyboard Test")
    # def mouse_event(event, x, y, flags, param):
    #     global mock_pointer_x_cam, mock_pointer_y_cam
    #     mock_pointer_x_cam = x
    #     mock_pointer_y_cam = y
    # cv2.setMouseCallback("Virtual Keyboard Test", mouse_event)

    print("Memulai tes keyboard virtual. Tutup jendela dengan 'q'.")
    print("Beberapa tombol spesial (Shift, Caps) akan mengubah tampilan tombol lain.")
    print("Hover di atas tombol untuk melihat efek. Klik (disimulasikan dengan 'c') akan mencoba 'menekan' tombol.")

    while True:
        test_frame = dummy_frame.copy() # Reset frame setiap iterasi
        
        # Gambar keyboard di frame
        test_frame_with_kb = keyboard.draw(test_frame, mock_pointer_x_cam, mock_pointer_y_cam)
        
        # Tampilkan kursor dummy di frame
        cv2.circle(test_frame_with_kb, (mock_pointer_x_cam, mock_pointer_y_cam), 5, (0,0,255), -1)

        cv2.imshow("Virtual Keyboard Test", test_frame_with_kb)
        
        key_press = cv2.waitKey(30) & 0xFF

        # Simulasikan gerakan pointer dengan tombol panah
        if key_press == ord('w'): mock_pointer_y_cam -= 10
        elif key_press == ord('s'): mock_pointer_y_cam += 10
        elif key_press == ord('a'): mock_pointer_x_cam -= 10
        elif key_press == ord('d'): mock_pointer_x_cam += 10
        
        # Simulasikan klik dengan tombol 'c'
        simulated_click = False
        if key_press == ord('c'):
            simulated_click = True
            print(f"\n--- Simulating CLICK at ({mock_pointer_x_cam}, {mock_pointer_y_cam}) ---")

        # Handle input keyboard
        # pointer_x_cam_abs dan pointer_y_cam_abs adalah koordinat di frame kamera
        char_typed = keyboard.handle_input(mock_pointer_x_cam, mock_pointer_y_cam, simulated_click)
        
        if char_typed:
            print(f"Tombol Ditekan/Aksi: {char_typed}")
            # Jika ini adalah aplikasi nyata, Anda akan mendapatkan karakter di sini.

        if key_press == ord('q'):
            break

    cv2.destroyAllWindows()