import cv2
import time
import pyautogui
from tracker import HandTracker, FaceTracker
from mouse_handler import MouseHandler

# --- PENGATURAN ---
CAM_INDEX = 0  # Ganti jika kamera Anda bukan default
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Untuk HandTracker
HAND_DETECTION_CONFIDENCE = 0.7
HAND_TRACKING_CONFIDENCE = 0.7
POINTER_LANDMARK_ID = 8  # Ujung Jari Telunjuk
CLICK_GESTURE_THRESHOLD = 35 # Jarak antara jari untuk klik (eksperimen!)

# Untuk FaceTracker
FACE_DETECTION_CONFIDENCE = 0.6
FACE_TRACKING_CONFIDENCE = 0.6
FACE_POINTER_LANDMARK_ID = 1 # Ujung Hidung

# Untuk MouseHandler
MOUSE_SMOOTHING = 0.3 # 0.1 (lebih lambat, halus) - 0.9 (lebih cepat, jerky)
ACTIVE_REGION_PADDING_PERCENT = 0.15 # Persentase padding dari tepi frame kamera

CLICK_COOLDOWN = 0.5 # Detik, untuk mencegah klik ganda

def main():
    # Inisialisasi Kamera
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print(f"Error: Tidak dapat membuka kamera dengan indeks {CAM_INDEX}")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    # Dapatkan dimensi frame aktual dari kamera
    cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Dimensi Kamera: {cam_width}x{cam_height}")

    # Inisialisasi Tracker
    hand_tracker = HandTracker(detection_con=HAND_DETECTION_CONFIDENCE, track_con=HAND_TRACKING_CONFIDENCE)
    face_tracker = FaceTracker(detection_con=FACE_DETECTION_CONFIDENCE, track_con=FACE_TRACKING_CONFIDENCE)

    # Inisialisasi Mouse Handler
    screen_width, screen_height = pyautogui.size()
    print(f"Dimensi Layar: {screen_width}x{screen_height}")
    mouse_handler = MouseHandler(screen_width, screen_height)
    mouse_handler.smoothing_factor = MOUSE_SMOOTHING

    # Variabel Status
    current_mode = "hand"  # "hand" atau "face"
    mouse_control_active = False
    last_click_time = 0

    print("\n--- KONTROL ---")
    print("'q': Keluar")
    print("'s': Start/Stop Kontrol Mouse")
    print("'h': Mode Tangan")
    print("'f': Mode Kepala")
    print("'c': Klik Kiri (jika dalam mode kepala atau gestur tangan gagal)")
    print("-----------------\n")


    while True:
        success, frame = cap.read()
        if not success:
            print("Gagal membaca frame dari kamera.")
            break

        # Balik frame secara horizontal (efek cermin)
        frame = cv2.flip(frame, 1)
        
        # Variabel untuk posisi landmark yang akan digunakan mouse
        pointer_x, pointer_y = -1, -1 
        gesture_detected = None

        if current_mode == "hand":
            frame, hand_results = hand_tracker.find_hands(frame, draw=True)
            if hand_results.multi_hand_landmarks:
                (pointer_x, pointer_y), lm_list = hand_tracker.get_landmark_position(frame, landmark_id=POINTER_LANDMARK_ID)
                if pointer_x != -1 and mouse_control_active:
                    # Gambar lingkaran pada landmark pointer
                    cv2.circle(frame, (pointer_x, pointer_y), 10, (255, 0, 255), cv2.FILLED)
                
                # Cek gestur klik jika kontrol mouse aktif dan cooldown terpenuhi
                if mouse_control_active and (time.time() - last_click_time > CLICK_COOLDOWN):
                    gesture_detected = hand_tracker.check_click_gesture(lm_list, CLICK_GESTURE_THRESHOLD)
                    if gesture_detected == "left_click":
                        mouse_handler.perform_click("left")
                        last_click_time = time.time()
                    # elif gesture_detected == "right_click": # Jika diimplementasikan
                    #     mouse_handler.perform_click("right")
                    #     last_click_time = time.time()


        elif current_mode == "face":
            frame, face_results = face_tracker.find_faces(frame, draw=False) # Draw false agar tidak terlalu ramai
            if face_results.multi_face_landmarks:
                (pointer_x, pointer_y) = face_tracker.get_landmark_position(frame, landmark_id=FACE_POINTER_LANDMARK_ID)
                if pointer_x != -1 and mouse_control_active:
                     # Gambar lingkaran pada landmark pointer
                    cv2.circle(frame, (pointer_x, pointer_y), 10, (0, 255, 0), cv2.FILLED)


        # Kontrol Mouse jika aktif dan landmark terdeteksi
        if mouse_control_active and pointer_x != -1:
            mouse_handler.move_mouse(pointer_x, pointer_y, cam_width, cam_height, ACTIVE_REGION_PADDING_PERCENT)

        # Tampilkan Status
        status_text = f"Mode: {current_mode.upper()} | Kontrol Mouse: {'AKTIF' if mouse_control_active else 'NONAKTIF'}"
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255) if mouse_control_active else (0, 255, 0), 2)
        if gesture_detected:
             cv2.putText(frame, f"Gestur: {gesture_detected}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)


        cv2.imshow("Mouse Tracker Tangan/Kepala", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Keluar dari aplikasi.")
            break
        elif key == ord('s'):
            mouse_control_active = not mouse_control_active
            print(f"Kontrol Mouse: {'Aktif' if mouse_control_active else 'Nonaktif'}")
            if mouse_control_active:
                # Reset posisi mouse sebelumnya saat diaktifkan agar tidak melompat
                px, py = pyautogui.position()
                mouse_handler.prev_x, mouse_handler.prev_y = px, py
        elif key == ord('h'):
            current_mode = "hand"
            print("Mode dialihkan ke: Tangan")
        elif key == ord('f'):
            current_mode = "face"
            print("Mode dialihkan ke: Kepala")
        elif key == ord('c'): # Tombol klik manual
            if mouse_control_active and (time.time() - last_click_time > CLICK_COOLDOWN):
                mouse_handler.perform_click("left")
                last_click_time = time.time()
                print("Klik manual (kiri) via tombol 'c'")


    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()