

import cv2
import mediapipe as mp
import math
import numpy as np # Diperlukan untuk kalkulasi EAR

class HandTracker:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.7):
        self.mode = mode
        self.max_hands = max_hands
        self.model_complexity = 1 # 0 or 1. Higher complexity = more accuracy, more latency.
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky tips
        # PIP joints (sendi tengah jari, penting untuk deteksi 'up')
        # Thumb (MCP:2), Index (PIP:6), Middle (PIP:10), Ring (PIP:14), Pinky (PIP:18)
        self.pip_ids = [2, 6, 10, 14, 18] 
        self.finger_names = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY"]
        self.landmark_list = [] # Menyimpan landmark list dari frame terakhir
        self.handedness = None # Menyimpan 'Left' or 'Right'

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        self.landmark_list = [] # Reset
        self.handedness = None

        if self.results.multi_hand_landmarks:
            for hand_idx, hand_lms in enumerate(self.results.multi_hand_landmarks):
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                
                if hand_idx == 0: 
                    current_hand_landmarks = []
                    for id_lm, lm in enumerate(hand_lms.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        current_hand_landmarks.append([id_lm, cx, cy, lm.z]) 
                    self.landmark_list = current_hand_landmarks

                    if self.results.multi_handedness:
                        # Pastikan handedness result sesuai dengan hand_idx
                        if hand_idx < len(self.results.multi_handedness):
                           self.handedness = self.results.multi_handedness[hand_idx].classification[0].label
                        else:
                            # Jika ada landmark tapi tidak ada handedness (jarang terjadi tapi untuk keamanan)
                            self.handedness = None 
        return img, self.results

    def get_landmark_position(self, landmark_id=8): 
        if self.landmark_list and landmark_id < len(self.landmark_list):
            return (self.landmark_list[landmark_id][1], self.landmark_list[landmark_id][2]), self.landmark_list
        return (-1, -1), []


    def fingers_up(self):
        """
        Mendeteksi jari mana yang terangkat.
        Mengembalikan list boolean [jempol, telunjuk, tengah, manis, kelingking].
        Jempol: Cek posisi X relatif terhadap pangkalnya (landmark 2).
        Jari lain: Cek posisi Y ujung jari relatif terhadap sendi PIP (landmark - 2 dari tip).
        """
        fingers = [False, False, False, False, False]
        if not self.landmark_list or not self.handedness or len(self.landmark_list) < max(self.tip_ids) +1:
            return fingers

        # Jempol (Thumb) - Landmark Tip: 4, Landmark Pangkal/Referensi: 2 (MCP) atau 3 (IP)
        # Kita gunakan tip (4) vs MCP (2) untuk orientasi X
        thumb_tip_x = self.landmark_list[self.tip_ids[0]][1] # lm_list[4][1]
        thumb_mcp_x = self.landmark_list[self.pip_ids[0]][1] # lm_list[2][1] (MCP)

        # Untuk deteksi jempol 'up', kita juga bisa cek jarak vertikalnya.
        # Jika jempol lebih tinggi (nilai Y lebih kecil) dari pangkal jari lain, mungkin itu 'up'.
        # Ini bisa lebih robust daripada hanya X, terutama jika tangan miring.
        # Mari coba dengan Y: Ujung jempol (4) lebih tinggi dari sendi pergelangan (0) atau pangkal telunjuk (5)
        thumb_tip_y = self.landmark_list[self.tip_ids[0]][2]
        index_finger_mcp_y = self.landmark_list[5][2] # MCP Jari Telunjuk

        # Kondisi Jempol 'Up' yang lebih baik:
        # 1. Untuk tangan kanan, ujung jempol (4) X < pangkal jempol (2) X. Untuk tangan kiri X > X.
        # 2. ATAU, ujung jempol (4) Y < pangkal jari telunjuk (5) Y (lebih tinggi secara vertikal)
        # Ini adalah heuristik, bisa disesuaikan.
        
        # Logika Jempol Awal (berdasarkan X)
        # if self.handedness == "Right":
        #     if thumb_tip_x < thumb_mcp_x: fingers[0] = True
        # elif self.handedness == "Left":
        #     if thumb_tip_x > thumb_mcp_x: fingers[0] = True

        # Logika Jempol Revisi (berdasarkan Y, ujung jempol lebih tinggi dari beberapa referensi)
        # Referensi: pertengahan antara MCP telunjuk (5) dan MCP kelingking (17)
        # Atau lebih simpel: jempol (4) Y lebih kecil dari jempol IP (3) Y.
        thumb_ip_y = self.landmark_list[self.tip_ids[0] - 1][2] # lm_list[3][2] (IP joint)
        if thumb_tip_y < thumb_ip_y:
             fingers[0] = True
        
        # 4 Jari lainnya (Telunjuk, Tengah, Manis, Kelingking)
        # Bandingkan posisi Y ujung jari (tip_ids[i]) dengan posisi Y dari sendi PIP (pip_ids[i])
        for i in range(1, 5): # Untuk jari telunjuk (1) hingga kelingking (4)
            finger_tip_y = self.landmark_list[self.tip_ids[i]][2]
            finger_pip_y = self.landmark_list[self.pip_ids[i]][2] 
            
            if finger_tip_y < finger_pip_y: # Ujung jari lebih tinggi (nilai Y lebih kecil)
                fingers[i] = True
        
        return fingers


    def calculate_distance(self, p1_id, p2_id):
        if not self.landmark_list or \
           p1_id >= len(self.landmark_list) or \
           p2_id >= len(self.landmark_list):
            return float('inf')
        
        p1 = self.landmark_list[p1_id]
        p2 = self.landmark_list[p2_id]
        return math.hypot(p2[1] - p1[1], p2[2] - p1[2])


    def get_gestures(self, click_threshold_distance=30):
        gestures = {
            "left_click": False,
            "right_click": False,
            "drag_toggle": False,
            "scroll_up": False,
            "scroll_down": False,
            "pointer_finger_id": self.tip_ids[1] 
        }
        if not self.landmark_list:
            return gestures

        # Gestur Pinch (Prioritas Tinggi)
        dist_index_thumb = self.calculate_distance(self.tip_ids[1], self.tip_ids[0])
        dist_middle_thumb = self.calculate_distance(self.tip_ids[2], self.tip_ids[0])
        dist_ring_thumb = self.calculate_distance(self.tip_ids[3], self.tip_ids[0])
        
        pinch_detected_this_frame = False
        if dist_index_thumb < click_threshold_distance:
            gestures["left_click"] = True
            pinch_detected_this_frame = True
        
        if not pinch_detected_this_frame and dist_middle_thumb < click_threshold_distance:
            gestures["right_click"] = True
            pinch_detected_this_frame = True
        
        if not pinch_detected_this_frame and dist_ring_thumb < click_threshold_distance:
            gestures["drag_toggle"] = True
            pinch_detected_this_frame = True

        # Gestur Scroll (Hanya jika tidak ada pinch terdeteksi)
        if not pinch_detected_this_frame:
            fingers_status = self.fingers_up() # [Thumb, Index, Middle, Ring, Pinky]
            
            # Scroll Atas: Jempol, Telunjuk, Tengah UP; Manis, Kelingking DOWN
            # Status:      [  True,   True,    True, False, False]
            if fingers_status == [True, True, True, False, False]:
                gestures["scroll_up"] = True
            
            # Scroll Bawah: Telunjuk, Tengah, Manis UP; Jempol, Kelingking DOWN
            # Status:       [ False,   True,    True,  True, False]
            elif fingers_status == [False, True, True, True, False]:
                gestures["scroll_down"] = True
        
        return gestures

# --- Sisa FaceTracker class tetap sama ---
class FaceTracker:
    def __init__(self, max_faces=1, detection_con=0.5, track_con=0.5):
        self.max_faces = max_faces
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=self.max_faces,
            refine_landmarks=True, 
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.LEFT_EYE_LANDMARKS_EAR = [33, 160, 158, 133, 153, 144] 
        self.RIGHT_EYE_LANDMARKS_EAR = [263, 387, 385, 362, 380, 373]

        self.left_blink_frames_count = 0
        self.right_blink_frames_count = 0
        self.raw_face_landmarks = None 

    def find_faces(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(img_rgb)
        self.raw_face_landmarks = None 

        if self.results.multi_face_landmarks:
            if len(self.results.multi_face_landmarks) > 0:
                 self.raw_face_landmarks = self.results.multi_face_landmarks[0].landmark 

            if draw: 
                for face_lms_normalized in self.results.multi_face_landmarks:
                    self.mp_draw.draw_landmarks(
                        image=img,
                        landmark_list=face_lms_normalized,
                        connections=self.mp_face_mesh.FACEMESH_TESSELATION, 
                        landmark_drawing_spec=None, 
                        connection_drawing_spec=self.mp_draw.DrawingSpec(color=(200,200,200), thickness=1, circle_radius=1)
                    )
        return img, self.results

    def get_landmark_position(self, img, landmark_id=1): 
        x_pos, y_pos = -1, -1
        if self.raw_face_landmarks and landmark_id < len(self.raw_face_landmarks):
            h, w, _ = img.shape
            lm = self.raw_face_landmarks[landmark_id]
            x_pos, y_pos = int(lm.x * w), int(lm.y * h)
        return (x_pos, y_pos)

    def _calculate_ear(self, eye_landmarks_coords):
        if len(eye_landmarks_coords) != 6:
            return 0.5 

        d_v1 = math.hypot(eye_landmarks_coords[1][0] - eye_landmarks_coords[5][0],  
                          eye_landmarks_coords[1][1] - eye_landmarks_coords[5][1])
        d_v2 = math.hypot(eye_landmarks_coords[2][0] - eye_landmarks_coords[4][0],  
                          eye_landmarks_coords[2][1] - eye_landmarks_coords[4][1])
        d_h = math.hypot(eye_landmarks_coords[0][0] - eye_landmarks_coords[3][0],   
                         eye_landmarks_coords[0][1] - eye_landmarks_coords[3][1])

        if d_h == 0: 
            return 0.5 
        
        ear = (d_v1 + d_v2) / (2.0 * d_h)
        return ear

    def get_face_gestures(self, img, ear_threshold=0.20, consecutive_frames_blink_needed=2):
        gestures = {
            "left_blink_detected": False,
            "right_blink_detected": False,
            "left_ear": 0.5, 
            "right_ear": 0.5
        }

        if not self.raw_face_landmarks:
            self.left_blink_frames_count = 0 
            self.right_blink_frames_count = 0
            return gestures

        h, w, _ = img.shape
        
        try:
            left_eye_coords = []
            for lm_id in self.LEFT_EYE_LANDMARKS_EAR:
                lm = self.raw_face_landmarks[lm_id]
                left_eye_coords.append((int(lm.x * w), int(lm.y * h)))
            
            right_eye_coords = []
            for lm_id in self.RIGHT_EYE_LANDMARKS_EAR:
                lm = self.raw_face_landmarks[lm_id]
                right_eye_coords.append((int(lm.x * w), int(lm.y * h)))
        except IndexError: 
            print("Peringatan: Landmark mata tidak lengkap untuk perhitungan EAR.")
            self.left_blink_frames_count = 0 
            self.right_blink_frames_count = 0
            return gestures


        left_ear = self._calculate_ear(left_eye_coords)
        right_ear = self._calculate_ear(right_eye_coords)
        gestures["left_ear"] = round(left_ear, 3)
        gestures["right_ear"] = round(right_ear, 3)

        if left_ear < ear_threshold:
            self.left_blink_frames_count += 1
        else:
            if self.left_blink_frames_count >= consecutive_frames_blink_needed:
                gestures["left_blink_detected"] = True
            self.left_blink_frames_count = 0 

        if right_ear < ear_threshold:
            self.right_blink_frames_count += 1
        else:
            if self.right_blink_frames_count >= consecutive_frames_blink_needed:
                gestures["right_blink_detected"] = True
            self.right_blink_frames_count = 0

        if gestures["left_blink_detected"]:
            self.left_blink_frames_count = 0 
        if gestures["right_blink_detected"]:
            self.right_blink_frames_count = 0

        return gestures