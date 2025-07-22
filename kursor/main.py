import cv2
import time
import pyautogui
import numpy as npf
import math 

from kursor.config import config_manager
from kursor.tracking.tracker import HandTracker, FaceTracker
from kursor.input.mouse_handler import MouseHandler
from kursor.input.virtual_keyboard import VirtualKeyboard # Import VirtualKeyboard

def print_instructions(settings):
    print("\n--- AURA MOUSE - KONTROL POINTER ---")
    print("  Pengaturan saat ini (sebagian):")
    print(f"    Mode Kontrol Awal: {settings.get('control_mode', 'N/A').upper()}")
    print(f"    Sensitivitas Mouse (Smoothing): {settings.get('mouse_sensitivity', 'N/A')}")
    print(f"    Durasi Dwell Click (Wajah): {settings.get('dwell_click_duration', 'N/A')} detik")
    print(f"    Deteksi Kedip (Wajah): {'Aktif' if settings.get('enable_blink_detection', False) else 'Nonaktif'}")
    print("\n  Kontrol Umum:")
    print("  'q': Keluar dari aplikasi")
    print("  's': Start/Stop Kontrol Mouse Aktual")
    print("  'h': Beralih ke Mode Deteksi TANGAN")
    print("  'f': Beralih ke Mode Deteksi KEPALA (Wajah)")
    print("  'p': Tampilkan instruksi ini lagi")
    print(f"  '{settings.get('keyboard_toggle_key', 'k')}': Toggle Keyboard Virtual") 
    print("\n  Gestur Mode TANGAN (umumnya):")
    print("  - Gerakkan Mouse: Ujung jari telunjuk (default)")
    print("  - Klik Kiri: Pertemukan jari TELUNJUK dan JEMPOL")
    print("  - Klik Kanan: Pertemukan jari TENGAH dan JEMPOL")
    print("  - Double Klik: Lakukan gestur Klik Kiri 2x dengan cepat")
    print("  - Toggle Drag: Pertemukan jari MANIS dan JEMPOL")
    print("  - Scroll Atas: Jempol, Telunjuk, Tengah UP; Manis, Kelingking DOWN (Contoh, lihat kode tracker.py)")
    print("  - Scroll Bawah: Telunjuk, Tengah, Manis UP; Jempol, Kelingking DOWN (Contoh, lihat kode tracker.py)")
    print("\n  Fitur Mode KEPALA (Wajah):")
    print("  - Gerakkan Mouse: Ujung hidung (default)")
    print("  - Klik Kiri (Dwell): Diamkan kursor")
    print(f"  - Aksi Kedip Kiri: {settings.get('face_blink_left_action', 'N/A')}")
    print(f"  - Aksi Kedip Kanan: {settings.get('face_blink_right_action', 'N/A')}")
    print("---------------------------------------\n")

def perform_action_from_string(action_string, mouse_handler_instance):
    if not action_string or action_string.lower() == "none":
        return False, "" 

    action_performed = False
    message = ""

    if action_string.lower() == "left_click":
        if mouse_handler_instance.left_click():
            action_performed = True
            message = "Klik Kiri (Kedip)"
    elif action_string.lower() == "right_click":
        if mouse_handler_instance.right_click():
            action_performed = True
            message = "Klik Kanan (Kedip)"
    elif action_string.lower() == "double_click":
        if mouse_handler_instance.double_click():
            action_performed = True
            message = "Double Klik (Kedip)"
    elif action_string.lower().startswith("scroll_up"):
        amount = mouse_handler_instance.default_scroll_amount 
        try: 
            amount = int(action_string.split('_')[-1])
        except (ValueError, IndexError): pass
        if mouse_handler_instance.scroll(amount):
            action_performed = True
            message = f"Scroll Atas {amount} (Kedip)"
    elif action_string.lower().startswith("scroll_down"):
        amount = -mouse_handler_instance.default_scroll_amount
        try:
            amount = -int(action_string.split('_')[-1])
        except (ValueError, IndexError): pass
        if mouse_handler_instance.scroll(amount):
            action_performed = True
            message = f"Scroll Bawah {abs(amount)} (Kedip)"
    elif action_string.lower().startswith("key_"): 
        key_to_press = action_string[4:]
        try:
            pyautogui.press(key_to_press)
            action_performed = True
            message = f"Tombol '{key_to_press.upper()}' (Kedip)"
            print(f"Aksi Kedip: Menekan tombol '{key_to_press}'")
        except Exception as e:
            print(f"Error menekan tombol '{key_to_press}' dari aksi kedip: {e}")
            message = f"Error Tombol (Kedip)"
    else:
        print(f"Aksi kedip tidak diketahui: {action_string}")
        message = f"Aksi Tdk Diketahui"

    return action_performed, message


def main():
    app_settings = config_manager.load_settings()

    CAM_INDEX = app_settings.get("camera_index", 0)
    FRAME_WIDTH = app_settings.get("frame_width", 640)
    FRAME_HEIGHT = app_settings.get("frame_height", 480)

    HAND_DETECTION_CONFIDENCE = app_settings.get("hand_detection_confidence", 0.75)
    HAND_TRACKING_CONFIDENCE = app_settings.get("hand_tracking_confidence", 0.75)
    POINTER_LANDMARK_ID_HAND = app_settings.get("hand_pointer_landmark", 8)
    BASE_CLICK_GESTURE_THRESHOLD = app_settings.get("click_gesture_threshold", 30) # Base threshold
    PINCH_STRICTNESS_FACTOR = app_settings.get("pinch_strictness_factor", 1.0)
    effective_click_gesture_threshold = BASE_CLICK_GESTURE_THRESHOLD * PINCH_STRICTNESS_FACTOR # Adjusted threshold
    DOUBLE_CLICK_INTERVAL = app_settings.get("double_click_interval", 0.3)
    THUMB_UP_OFFSET = app_settings.get("thumb_up_sensitivity_y_offset", 0)
    FINGER_UP_OFFSET = app_settings.get("finger_up_sensitivity_y_offset", 0)
    DEBUG_GESTURE_LOGGING = app_settings.get("debug_gesture_logging", False)


    FACE_DETECTION_CONFIDENCE = app_settings.get("face_detection_confidence", 0.6)
    FACE_TRACKING_CONFIDENCE = app_settings.get("face_tracking_confidence", 0.6)
    POINTER_LANDMARK_ID_FACE = app_settings.get("face_pointer_landmark", 1)
    DWELL_TIME_THRESHOLD = app_settings.get("dwell_click_duration", 1.0)
    ENABLE_BLINK_DETECTION = app_settings.get("enable_blink_detection", False)
    FACE_EAR_THRESHOLD = app_settings.get("face_eye_aspect_ratio_threshold", 0.20)
    FACE_BLINK_CONSECUTIVE_FRAMES = app_settings.get("face_blink_consecutive_frames", 2)
    FACE_BLINK_LEFT_ACTION = app_settings.get("face_blink_left_action", "left_click")
    FACE_BLINK_RIGHT_ACTION = app_settings.get("face_blink_right_action", "right_click")

    MOUSE_SMOOTHING_FACTOR = app_settings.get("mouse_sensitivity", 0.3)
    ACTIVE_REGION_PADDING_PERCENT = app_settings.get("active_region_padding", 0.10)
    SCROLL_UNITS = app_settings.get("scroll_amount", 100)
    ACTION_COOLDOWN_DEFAULT = app_settings.get("action_cooldown_default", 0.3)
    ACTION_COOLDOWN_SCROLL = app_settings.get("action_cooldown_scroll", 0.1)

    current_control_mode = app_settings.get("control_mode", "hand")
    mouse_control_active = False

    last_left_click_time_hand = 0
    dwell_start_time_face = 0
    pointer_at_dwell_start_x_face, pointer_at_dwell_start_y_face = -1, -1
    dwell_click_triggered_face = False
    
    print_instructions(app_settings)

    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print(f"Error: Tidak dapat membuka kamera dengan indeks {CAM_INDEX}. Coba indeks lain atau periksa koneksi kamera.")
        if CAM_INDEX != 0:
            print("Mencoba kamera indeks 0 sebagai fallback...")
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                print("Fallback ke kamera indeks 0 berhasil.")
                CAM_INDEX = 0 
            else:
                print("Gagal membuka kamera indeks 0 juga.")
                return
        else:
            return 
            
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cam_actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Kamera berhasil dibuka: Indeks {CAM_INDEX}, Resolusi {cam_actual_width}x{cam_actual_height}")

    hand_tracker = HandTracker(
        detection_con=HAND_DETECTION_CONFIDENCE, 
        track_con=HAND_TRACKING_CONFIDENCE,
        thumb_up_sensitivity_y_offset=THUMB_UP_OFFSET,
        finger_up_sensitivity_y_offset=FINGER_UP_OFFSET
    )
    face_tracker = FaceTracker(detection_con=FACE_DETECTION_CONFIDENCE, track_con=FACE_TRACKING_CONFIDENCE)

    screen_width, screen_height = pyautogui.size()
    print(f"Resolusi Layar: {screen_width}x{screen_height}")
    mouse_handler = MouseHandler(screen_width, screen_height, default_scroll=SCROLL_UNITS)
    mouse_handler.smoothing_factor = MOUSE_SMOOTHING_FACTOR
    mouse_handler.set_action_cooldowns(default=ACTION_COOLDOWN_DEFAULT, scroll=ACTION_COOLDOWN_SCROLL)

    # Inisialisasi Keyboard Virtual
    keyboard_visible = app_settings.get("keyboard_show_on_startup", False)
    vkeyboard = VirtualKeyboard(
        screen_width=screen_width, # Pass screen dimensions for reference if needed by keyboard
        screen_height=screen_height,
        layout_name=app_settings.get("keyboard_layout", "qwerty_id"),
        theme_name=app_settings.get("keyboard_theme", "light"),
        key_sound_enabled=app_settings.get("keyboard_key_sound", False),
        dwell_time=app_settings.get("keyboard_dwell_time", 0.7)
    )
    vkeyboard.set_visibility(keyboard_visible)
    KEYBOARD_TOGGLE_KEY = app_settings.get("keyboard_toggle_key", "k")


    prev_time = 0 
    while True:
        success, frame_original = cap.read()
        if not success:
            print("Gagal membaca frame dari kamera. Aplikasi berhenti.")
            break

        current_time_fps = time.time()
        fps = 1 / (current_time_fps - prev_time) if (current_time_fps - prev_time) > 0 else 0
        prev_time = current_time_fps

        frame = cv2.flip(frame_original, 1)
        
        current_pointer_x_cam, current_pointer_y_cam = -1, -1 
        info_message_display = ""
        action_performed_this_frame = False 
        raw_click_gesture_for_keyboard = False # Signal for keyboard if a primary click gesture occurs

        if current_control_mode == "hand":
            frame_processed, _ = hand_tracker.find_hands(frame, draw=True) 
            
            if hand_tracker.landmark_list: 
                (raw_px, raw_py), _ = hand_tracker.get_landmark_position(landmark_id=POINTER_LANDMARK_ID_HAND)
                
                if raw_px != -1:
                    current_pointer_x_cam, current_pointer_y_cam = raw_px, raw_py
                    cv2.circle(frame, (current_pointer_x_cam, current_pointer_y_cam), 10, (255, 0, 255), cv2.FILLED)

                    if mouse_control_active: # Removed 'not action_performed_this_frame' for now to get raw gesture for keyboard
                        hand_gestures = hand_tracker.get_gestures(
                            click_threshold_distance=effective_click_gesture_threshold,
                            debug_logging=DEBUG_GESTURE_LOGGING
                        )
                        
                        if hand_gestures.get("left_click", False):
                             raw_click_gesture_for_keyboard = True # Left pinch is a primary click for keyboard

                        if not action_performed_this_frame: # Process mouse actions only if not already done
                            current_time_action = time.time()
                            if hand_gestures.get("left_click", False) and (current_time_action - last_left_click_time_hand) < DOUBLE_CLICK_INTERVAL:
                                if mouse_handler.double_click():
                                    info_message_display = "Double Klik Tangan"
                                    action_performed_this_frame = True
                                last_left_click_time_hand = 0 
                            elif hand_gestures.get("left_click", False): # Not a double click
                                if mouse_handler.left_click():
                                    info_message_display = "Klik Kiri Tangan"
                                    action_performed_this_frame = True
                                last_left_click_time_hand = current_time_action # Set for potential double click
                            
                            if not action_performed_this_frame and hand_gestures.get("right_click", False):
                                if mouse_handler.right_click():
                                    info_message_display = "Klik Kanan Tangan"
                                    action_performed_this_frame = True
                            
                            if not action_performed_this_frame and hand_gestures.get("drag_toggle", False):
                                if mouse_handler.toggle_drag():
                                    drag_status = "AKTIF" if mouse_handler.is_dragging else "NONAKTIF"
                                    info_message_display = f"Drag Tangan: {drag_status}"
                                    action_performed_this_frame = True
                            
                            if not action_performed_this_frame and hand_gestures.get("scroll_up", False):
                                if mouse_handler.scroll(SCROLL_UNITS): 
                                    info_message_display = "Scroll Atas Tangan"
                                    action_performed_this_frame = True
                            
                            if not action_performed_this_frame and hand_gestures.get("scroll_down", False):
                                if mouse_handler.scroll(-SCROLL_UNITS): 
                                    info_message_display = "Scroll Bawah Tangan"
                                    action_performed_this_frame = True
            else: 
                last_left_click_time_hand = 0


        elif current_control_mode == "face":
            frame_processed, _ = face_tracker.find_faces(frame, draw=True) 
            dwell_reset_threshold = BASE_CLICK_GESTURE_THRESHOLD / 2 # Using base threshold for consistency

            if face_tracker.raw_face_landmarks: 
                (raw_px, raw_py) = face_tracker.get_landmark_position(frame, landmark_id=POINTER_LANDMARK_ID_FACE)

                if raw_px != -1:
                    current_pointer_x_cam, current_pointer_y_cam = raw_px, raw_py
                    cv2.circle(frame, (current_pointer_x_cam, current_pointer_y_cam), 10, (0, 255, 0), cv2.FILLED)

                    if mouse_control_active: # Removed 'not action_performed_this_frame'
                        # Dwell Click Logic
                        if pointer_at_dwell_start_x_face == -1: 
                            pointer_at_dwell_start_x_face = current_pointer_x_cam
                            pointer_at_dwell_start_y_face = current_pointer_y_cam
                            dwell_start_time_face = time.time()
                            dwell_click_triggered_face = False
                        else:
                            distance_moved_from_dwell_start = math.hypot(
                                current_pointer_x_cam - pointer_at_dwell_start_x_face,
                                current_pointer_y_cam - pointer_at_dwell_start_y_face
                            )
                            if distance_moved_from_dwell_start > dwell_reset_threshold:
                                pointer_at_dwell_start_x_face = -1 
                                dwell_click_triggered_face = False
                            elif not dwell_click_triggered_face and (time.time() - dwell_start_time_face > DWELL_TIME_THRESHOLD):
                                raw_click_gesture_for_keyboard = True # Dwell complete is a primary click
                                if not action_performed_this_frame:
                                    if mouse_handler.left_click():
                                        info_message_display = "Dwell Klik Kiri (Wajah)"
                                        action_performed_this_frame = True
                                dwell_click_triggered_face = True 
                                pointer_at_dwell_start_x_face = -1
                        
                        if pointer_at_dwell_start_x_face != -1 and not dwell_click_triggered_face:
                            elapsed_dwell_time = time.time() - dwell_start_time_face
                            dwell_progress_ratio = min(elapsed_dwell_time / DWELL_TIME_THRESHOLD, 1.0)
                            cv2.circle(frame, 
                                       (pointer_at_dwell_start_x_face, pointer_at_dwell_start_y_face), 
                                       int((dwell_reset_threshold + 5) * dwell_progress_ratio), 
                                       (0, 255, 255), 2) 

                        # Blink Detection Logic
                        if not action_performed_this_frame and ENABLE_BLINK_DETECTION:
                            face_gestures = face_tracker.get_face_gestures(
                                frame, 
                                ear_threshold=FACE_EAR_THRESHOLD,
                                consecutive_frames_blink_needed=FACE_BLINK_CONSECUTIVE_FRAMES
                            )
                            
                            if face_gestures.get("left_blink_detected", False):
                                # Left blink can also be a primary click for keyboard if configured
                                if FACE_BLINK_LEFT_ACTION.lower() == "left_click":
                                    raw_click_gesture_for_keyboard = True
                                blink_action_performed, blink_message = perform_action_from_string(FACE_BLINK_LEFT_ACTION, mouse_handler)
                                if blink_action_performed:
                                    info_message_display = blink_message
                                    action_performed_this_frame = True
                            
                            if not action_performed_this_frame and face_gestures.get("right_blink_detected", False):
                                if FACE_BLINK_RIGHT_ACTION.lower() == "left_click": # If right blink also configured for left_click
                                    raw_click_gesture_for_keyboard = True
                                blink_action_performed, blink_message = perform_action_from_string(FACE_BLINK_RIGHT_ACTION, mouse_handler)
                                if blink_action_performed:
                                    info_message_display = blink_message
                                    action_performed_this_frame = True
            else: 
                pointer_at_dwell_start_x_face = -1
                dwell_click_triggered_face = False
                face_tracker.left_blink_frames_count = 0 
                face_tracker.right_blink_frames_count = 0


        keyboard_input_consumed_click = False
        if vkeyboard.is_visible:
            # Pass raw_click_gesture for keyboard to attempt typing/action
            # If keyboard types, it might set action_performed_this_frame to true
            vkeyboard.handle_input(pyautogui.position()[0], pyautogui.position()[1],
                                                raw_click_gesture_for_keyboard and mouse_control_active) 


        if mouse_control_active and current_pointer_x_cam != -1 and not keyboard_input_consumed_click:
            # Only move mouse if keyboard didn't "consume" the pointer interaction leading to a type
            # or if no click was involved (just movement)
            mouse_handler.move_mouse(
                current_pointer_x_cam, current_pointer_y_cam,
                cam_actual_width, cam_actual_height,
                ACTIVE_REGION_PADDING_PERCENT
            )

        if vkeyboard.is_visible:
            vkeyboard.draw(frame, current_pointer_x_cam, current_pointer_y_cam)

        status_line1 = f"Mode: {current_control_mode.upper()} | Mouse: {'ON' if mouse_control_active else 'OFF'}"
        cv2.putText(frame, status_line1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                    (0, 0, 255) if mouse_control_active else (0, 128, 0), 2)
        
        cv2.putText(frame, f"FPS: {int(fps)}", (cam_actual_width - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        if mouse_handler.is_dragging:
             cv2.putText(frame, "DRAG", (cam_actual_width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,100,0), 2)
        
        if info_message_display:
             # Prioritize keyboard message if it exists
             if "Ketik:" in info_message_display:
                 cv2.putText(frame, info_message_display, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
             else:
                 cv2.putText(frame, f"Aksi: {info_message_display}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)


        cv2.imshow("AuraMouse - Kontrol Pointer", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            mouse_control_active = not mouse_control_active
            print(f"Kontrol Mouse Aktual: {'Aktif' if mouse_control_active else 'Nonaktif'}")
            if mouse_control_active:
                current_screen_mouse_x, current_screen_mouse_y = pyautogui.position()
                mouse_handler.prev_x = current_screen_mouse_x
                mouse_handler.prev_y = current_screen_mouse_y
            else:
                if mouse_handler.is_dragging: mouse_handler.toggle_drag() 
        elif key == ord('h'):
            if current_control_mode != "hand":
                current_control_mode = "hand"
                app_settings["control_mode"] = "hand" 
                if mouse_handler.is_dragging: mouse_handler.toggle_drag()
                pointer_at_dwell_start_x_face = -1 
                print("Mode dialihkan ke: TANGAN")
        elif key == ord('f'):
            if current_control_mode != "face":
                current_control_mode = "face"
                app_settings["control_mode"] = "face"
                if mouse_handler.is_dragging: mouse_handler.toggle_drag()
                last_left_click_time_hand = 0 
                print("Mode dialihkan ke: KEPALA (Wajah)")
        elif key == ord('p'):
            print_instructions(app_settings)
        elif key == ord(KEYBOARD_TOGGLE_KEY.lower()): 
            keyboard_visible = not keyboard_visible
            vkeyboard.set_visibility(keyboard_visible)
            print(f"Keyboard Virtual: {'Tampil' if keyboard_visible else 'Sembunyi'}")

    print("Membersihkan sumber daya...")
    if vkeyboard.is_alive():
        vkeyboard.root.quit()
    cap.release()
    cv2.destroyAllWindows()
    
    # config_manager.save_settings(app_settings) 

if __name__ == "__main__":
    main()