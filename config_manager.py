

import json
import os

CONFIG_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "app_version": "0.2.0", # Version bump
    "control_mode": "hand",  # "hand" or "face"
    
    # Mouse & Pointer
    "camera_index": 0, # Added from main.py's DEFAULT_CAM_INDEX
    "frame_width": 640,
    "frame_height": 480,
    "mouse_sensitivity": 0.3, # Smoothing factor 0.1 (more smooth) - 1.0 (less smooth)
    "dwell_click_duration": 1.0, # detik, untuk klik wajah
    "active_region_padding": 0.10, # persen
    "scroll_amount": 100, # Unit scroll

    # Hand Gestures
    "hand_detection_confidence": 0.75,
    "hand_tracking_confidence": 0.75,
    "hand_pointer_landmark": 8, # Ujung telunjuk
    "click_gesture_threshold": 30, # piksel, untuk pinch
    "double_click_interval": 0.3, # detik
    # Definisi gestur scroll bisa lebih kompleks, untuk sekarang pakai setting dari tracker
    # "hand_scroll_gesture_up": "INDEX_MIDDLE_UP", 
    # "hand_scroll_gesture_down": "RING_PINKY_UP", # Contoh, implementasi di tracker.py
    "hand_scroll_pinch_thumb_threshold": 40, # Jarak pinch jempol untuk scroll, mungkin beda dari klik

    # Face Gestures
    "face_detection_confidence": 0.6,
    "face_tracking_confidence": 0.6,
    "face_pointer_landmark": 1, # Ujung hidung
    "enable_blink_detection": False,
    "face_blink_left_action": "left_click", # "left_click", "right_click", "none", "key_F1", etc.
    "face_blink_right_action": "right_click",
    "face_eye_aspect_ratio_threshold": 0.20, # Threshold untuk EAR
    "face_blink_consecutive_frames": 2, # Jumlah frame berturut-turut EAR < threshold untuk dianggap kedip

    # Virtual Keyboard
    "keyboard_show_on_startup": False,
    "keyboard_layout": "qwerty_id", # "qwerty_id", "qwerty_en", "azerty_fr", "numeric"
    "keyboard_theme": "light", # "light", "dark", "custom"
    "keyboard_dwell_time": 0.7, # detik, untuk dwell pada tombol keyboard
    "keyboard_key_sound": False,
    "keyboard_toggle_key": "k", # Tombol untuk menampilkan/menyembunyikan keyboard

    # UI/App
    "theme": "light", # Tema GUI pengaturan
    "action_cooldown_default": 0.3, # Cooldown umum untuk aksi mouse
    "action_cooldown_scroll": 0.1  # Cooldown khusus untuk scroll
}

def save_settings(settings):
    """Menyimpan dictionary settings ke file JSON."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=4, sort_keys=True) # sort_keys for consistency
        print(f"Pengaturan disimpan ke {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error menyimpan pengaturan: {e}")
        return False

def load_settings():
    """Memuat settings dari file JSON. Jika tidak ada, buat default."""
    settings_to_return = DEFAULT_SETTINGS.copy() # Mulai dengan default

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_settings_from_file = json.load(f)
                
                # Gabungkan dengan default: ambil nilai dari file jika ada, jika tidak pakai default
                # Ini juga memastikan kunci baru dari DEFAULT_SETTINGS ditambahkan jika file lama
                for key in settings_to_return:
                    if key in loaded_settings_from_file:
                        settings_to_return[key] = loaded_settings_from_file[key]
                
                # Cek apakah ada kunci di file yang tidak ada di default (mungkin dari versi lama)
                # dan tambahkan ke settings_to_return agar tidak hilang (opsional, tergantung strategi)
                for key in loaded_settings_from_file:
                    if key not in settings_to_return:
                         settings_to_return[key] = loaded_settings_from_file[key]
                         # print(f"Peringatan: Kunci '{key}' ada di {CONFIG_FILE} tapi tidak di DEFAULT_SETTINGS.")


                print(f"Pengaturan dimuat dan digabungkan dari {CONFIG_FILE}")
                
                # Jika ada perubahan struktur (misal, kunci baru ditambahkan dari default), simpan kembali file
                # agar file settings.json selalu up-to-date dengan semua kunci yang diketahui aplikasi.
                # Ini penting jika DEFAULT_SETTINGS adalah "master" dari semua kunci yang mungkin.
                # Periksa apakah settings yang akan dikembalikan berbeda dari yang ada di file.
                # Cara sederhana: save ulang jika jumlah kunci berbeda atau ada kunci baru.
                if len(settings_to_return.keys()) != len(loaded_settings_from_file.keys()) or \
                   any(k not in loaded_settings_from_file for k in DEFAULT_SETTINGS.keys()):
                    print(f"Memperbarui {CONFIG_FILE} dengan kunci baru/default yang mungkin hilang.")
                    save_settings(settings_to_return)

                return settings_to_return
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON dari {CONFIG_FILE}: {e}. Menggunakan default dan mencoba membuat file baru.")
            save_settings(settings_to_return) # Simpan default yang bersih
            return settings_to_return
        except Exception as e:
            print(f"Error umum saat memuat pengaturan dari {CONFIG_FILE}, menggunakan default: {e}")
            # Jika file korup atau error lain, coba simpan default baru
            save_settings(settings_to_return)
            return settings_to_return
    else:
        print(f"{CONFIG_FILE} tidak ditemukan, membuat pengaturan default.")
        save_settings(settings_to_return)
        return settings_to_return

if __name__ == '__main__':
    # Contoh penggunaan
    current_settings = load_settings()
    print("\nPengaturan Saat Ini (setelah load/merge):")
    for k, v in sorted(current_settings.items()):
        print(f"  {k}: {v}")

    # Contoh modifikasi dan simpan
    # current_settings["mouse_sensitivity"] = 0.55
    # current_settings["new_temporary_key"] = "test_value" # Kunci ini akan ditambahkan
    # save_settings(current_settings)

    # loaded_again = load_settings()
    # print("\nPengaturan Setelah Update (jika ada):")
    # for k, v in sorted(loaded_again.items()):
    #     print(f"  {k}: {v}")

    # print("\nDEFAULT_SETTINGS (untuk perbandingan):")
    # for k, v in sorted(DEFAULT_SETTINGS.items()):
    #     print(f"  {k}: {v}")