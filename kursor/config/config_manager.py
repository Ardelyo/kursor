import json
import os

CONFIG_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "app_version": "0.2.1", # Version bump for new features
    "control_mode": "hand",  # "hand" or "face"
    
    # Mouse & Pointer
    "camera_index": 0, 
    "frame_width": 640,
    "frame_height": 480,
    "mouse_sensitivity": 0.3, 
    "dwell_click_duration": 1.0, 
    "active_region_padding": 0.10, 
    "scroll_amount": 100, 

    # Hand Gestures
    "hand_detection_confidence": 0.75,
    "hand_tracking_confidence": 0.75,
    "hand_pointer_landmark": 8, 
    "click_gesture_threshold": 30, 
    "double_click_interval": 0.3, 
    "hand_scroll_pinch_thumb_threshold": 40, 
    "thumb_up_sensitivity_y_offset": 5, # Pixels, positive makes it easier to detect "up"
    "finger_up_sensitivity_y_offset": 5, # Pixels, positive makes it easier to detect "up"
    "pinch_strictness_factor": 1.0, # Multiplier for click_gesture_threshold. <1 easier, >1 stricter.
    "debug_gesture_logging": False, # Enable detailed gesture logging in console

    # Face Gestures
    "face_detection_confidence": 0.6,
    "face_tracking_confidence": 0.6,
    "face_pointer_landmark": 1, 
    "enable_blink_detection": False,
    "face_blink_left_action": "left_click", 
    "face_blink_right_action": "right_click",
    "face_eye_aspect_ratio_threshold": 0.20, 
    "face_blink_consecutive_frames": 2, 

    # Virtual Keyboard
    "keyboard_show_on_startup": False,
    "keyboard_layout": "qwerty_id", 
    "keyboard_theme": "light", 
    "keyboard_dwell_time": 0.7, 
    "keyboard_key_sound": False,
    "keyboard_toggle_key": "k", 

    # UI/App
    "theme": "light", 
    "action_cooldown_default": 0.3, 
    "action_cooldown_scroll": 0.1  
}

def save_settings(settings):
    """Menyimpan dictionary settings ke file JSON."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=4, sort_keys=True) 
        print(f"Pengaturan disimpan ke {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error menyimpan pengaturan: {e}")
        return False

def load_settings():
    """Memuat settings dari file JSON. Jika tidak ada, buat default."""
    settings_to_return = DEFAULT_SETTINGS.copy() 

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_settings_from_file = json.load(f)
                
                current_default_keys = set(settings_to_return.keys())
                file_keys = set(loaded_settings_from_file.keys())

                # Update from file if key exists in default
                for key in current_default_keys:
                    if key in loaded_settings_from_file:
                        settings_to_return[key] = loaded_settings_from_file[key]
                
                # Add keys from file that are not in current defaults (e.g. user added, or from older version of app)
                # This behavior can be debated. For now, we'll add them to preserve them.
                # If a key was removed from DEFAULT_SETTINGS, it will persist if it's in the file.
                for key in file_keys:
                    if key not in current_default_keys:
                         settings_to_return[key] = loaded_settings_from_file[key]
                         # print(f"Peringatan: Kunci '{key}' ada di {CONFIG_FILE} tapi tidak di DEFAULT_SETTINGS saat ini.")
                
                print(f"Pengaturan dimuat dan digabungkan dari {CONFIG_FILE}")
                
                # Check if the file needs to be updated with new default keys
                # or if the structure of what's returned significantly differs from the file
                # (e.g., new keys were added from DEFAULT_SETTINGS that weren't in the file).
                resaved_needed = False
                if len(settings_to_return.keys()) > len(file_keys): # New keys added from defaults
                    resaved_needed = True
                
                # Also check if any key from current DEFAULT_SETTINGS is missing in the loaded file
                # (meaning a new default was added and the file is old)
                for default_key in current_default_keys:
                    if default_key not in file_keys:
                        resaved_needed = True
                        break # No need to check further

                if resaved_needed:
                    print(f"Memperbarui {CONFIG_FILE} dengan kunci baru/default yang mungkin hilang.")
                    save_settings(settings_to_return) # Save the merged and potentially updated settings

                return settings_to_return
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON dari {CONFIG_FILE}: {e}. Menggunakan default dan mencoba membuat file baru.")
            save_settings(settings_to_return) 
            return settings_to_return
        except Exception as e:
            print(f"Error umum saat memuat pengaturan dari {CONFIG_FILE}, menggunakan default: {e}")
            save_settings(settings_to_return)
            return settings_to_return
    else:
        print(f"{CONFIG_FILE} tidak ditemukan, membuat pengaturan default.")
        save_settings(settings_to_return)
        return settings_to_return

if __name__ == '__main__':
    current_settings = load_settings()
    print("\nPengaturan Saat Ini (setelah load/merge):")
    for k, v in sorted(current_settings.items()):
        print(f"  {k}: {v}")

    # Example: Force update of a setting to test saving
    # current_settings["app_version"] = "0.2.1-test"
    # save_settings(current_settings)