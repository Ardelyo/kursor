import cv2
import mediapipe as mp
import math

class HandTracker:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.7):
        self.mode = mode
        self.max_hands = max_hands
        # Kompleksitas model, 0 atau 1. Diabaikan jika mode statis.
        self.model_complexity = 1  # Sesuaikan jika perlu
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
        self.tip_ids = [4, 8, 12, 16, 20] # ID landmark ujung jari (jempol, telunjuk, tengah, manis, kelingking)

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img, self.results

    def get_landmark_position(self, img, hand_no=0, landmark_id=8): # Default: ujung jari telunjuk
        lm_list = []
        x_pos, y_pos = -1, -1
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
                if id == landmark_id:
                    x_pos, y_pos = cx, cy
        return (x_pos, y_pos), lm_list

    def check_click_gesture(self, lm_list, click_threshold_distance=30):
        if len(lm_list) != 0:
            # Jarak antara ujung jari telunjuk (8) dan ujung ibu jari (4)
            x1, y1 = lm_list[self.tip_ids[1]][1], lm_list[self.tip_ids[1]][2] # Telunjuk
            x2, y2 = lm_list[self.tip_ids[0]][1], lm_list[self.tip_ids[0]][2] # Jempol
            
            # Jarak antara ujung jari tengah (12) dan ujung ibu jari (4)
            x3, y3 = lm_list[self.tip_ids[2]][1], lm_list[self.tip_ids[2]][2] # Tengah

            distance_index_thumb = math.hypot(x2 - x1, y2 - y1)
            distance_middle_thumb = math.hypot(x2 - x3, y2 - y3)

            # Klik kiri: telunjuk dan jempol bertemu
            if distance_index_thumb < click_threshold_distance:
                return "left_click"
            # Klik kanan: jari tengah dan jempol bertemu (opsional, bisa disesuaikan)
            # elif distance_middle_thumb < click_threshold_distance:
            #     return "right_click"
                
        return None

class FaceTracker:
    def __init__(self, max_faces=1, detection_con=0.5, track_con=0.5):
        self.max_faces = max_faces
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=self.max_faces,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_draw.DrawingSpec(thickness=1, circle_radius=1)

    def find_faces(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(img_rgb)
        
        if self.results.multi_face_landmarks:
            for face_lms in self.results.multi_face_landmarks:
                if draw:
                    # Menggambar hanya landmark, bukan mesh lengkap untuk kejelasan
                    # self.mp_draw.draw_landmarks(
                    #     image=img,
                    #     landmark_list=face_lms,
                    #     connections=self.mp_face_mesh.FACEMESH_TESSELATION, #FACEMESH_CONTOURS
                    #     landmark_drawing_spec=self.drawing_spec,
                    #     connection_drawing_spec=self.drawing_spec)
                    pass # Tidak menggambar agar lebih fokus pada titik hidung
        return img, self.results

    def get_landmark_position(self, img, face_no=0, landmark_id=1): # Default: ujung hidung (landmark 1)
        x_pos, y_pos = -1, -1
        if self.results.multi_face_landmarks:
            face = self.results.multi_face_landmarks[face_no]
            h, w, c = img.shape
            # Dapatkan landmark tertentu
            lm = face.landmark[landmark_id]
            x_pos, y_pos = int(lm.x * w), int(lm.y * h)
        return (x_pos, y_pos)