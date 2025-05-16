import cv2
import mediapipe as mp
import math
import numpy as np 

class HandTracker:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.7,
                 thumb_up_sensitivity_y_offset=0, finger_up_sensitivity_y_offset=0): # Added sensitivity params
        self.mode = mode
        self.max_hands = max_hands
        self.model_complexity = 1 
        self.detection_con = detection_con
        self.track_con = track_con

        self.thumb_up_sensitivity_y_offset = thumb_up_sensitivity_y_offset
        self.finger_up_sensitivity_y_offset = finger_up_sensitivity_y_offset

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20] 
        self.pip_ids = [2, 6, 10, 14, 18] 
        self.finger_names = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY"]
        self.landmark_list = [] 
        self.handedness = None 

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        self.landmark_list = [] 
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
                        if hand_idx < len(self.results.multi_handedness):
                           self.handedness = self.results.multi_handedness[hand_idx].classification[0].label
                        else:
                            self.handedness = None 
        return img, self.results

    def get_landmark_position(self, landmark_id=8): 
        if self.landmark_list and landmark_id < len(self.landmark_list):
            return (self.landmark_list[landmark_id][1], self.landmark_list[landmark_id][2]), self.landmark_list
        return (-1, -1), []


    def fingers_up(self, debug_logging=False): # Added debug_logging
        """
        Mendeteksi jari mana yang terangkat.
        Menggunakan self.thumb_up_sensitivity_y_offset dan self.finger_up_sensitivity_y_offset.
        Positive offset makes it easier for the finger to be considered "up".
        """
        fingers = [False, False, False, False, False]
        if not self.landmark_list or not self.handedness or len(self.landmark_list) < max(self.tip_ids) +1:
            if debug_logging: print("[FingersUp] No landmarks, handedness, or insufficient landmarks.")
            return fingers

        thumb_tip_y = self.landmark_list[self.tip_ids[0]][2]
        thumb_ip_y = self.landmark_list[self.tip_ids[0] - 1][2] # lm_list[3][2] (IP joint)
        
        # Thumb: tip_y < (ip_y + offset). Positive offset allows tip_y to be slightly larger (lower on screen)
        # and still be considered "up" relative to the IP joint.
        if thumb_tip_y < (thumb_ip_y + self.thumb_up_sensitivity_y_offset):
             fingers[0] = True
        
        if debug_logging:
            print(f"[FingersUp] Thumb: TipY({thumb_tip_y}), IP_Y({thumb_ip_y}), Offset({self.thumb_up_sensitivity_y_offset}), Up={fingers[0]}")

        for i in range(1, 5): 
            finger_tip_y = self.landmark_list[self.tip_ids[i]][2]
            finger_pip_y = self.landmark_list[self.pip_ids[i]][2] 
            
            # Other fingers: tip_y < (pip_y + offset)
            if finger_tip_y < (finger_pip_y + self.finger_up_sensitivity_y_offset): 
                fingers[i] = True
            
            if debug_logging:
                 print(f"[FingersUp] {self.finger_names[i]}: TipY({finger_tip_y}), PIP_Y({finger_pip_y}), Offset({self.finger_up_sensitivity_y_offset}), Up={fingers[i]}")
        
        if debug_logging: print(f"[FingersUp] Final status: {fingers}")
        return fingers


    def calculate_distance(self, p1_id, p2_id):
        if not self.landmark_list or \
           p1_id >= len(self.landmark_list) or \
           p2_id >= len(self.landmark_list):
            return float('inf')
        
        p1 = self.landmark_list[p1_id]
        p2 = self.landmark_list[p2_id]
        return math.hypot(p2[1] - p1[1], p2[2] - p1[2])


    def get_gestures(self, click_threshold_distance=30, debug_logging=False): # Added debug_logging
        gestures = {
            "left_click": False,
            "right_click": False,
            "drag_toggle": False,
            "scroll_up": False,
            "scroll_down": False,
            "pointer_finger_id": self.tip_ids[1] 
        }
        if not self.landmark_list:
            if debug_logging: print("[GetGestures] No landmarks for gesture detection.")
            return gestures

        dist_index_thumb = self.calculate_distance(self.tip_ids[1], self.tip_ids[0])
        dist_middle_thumb = self.calculate_distance(self.tip_ids[2], self.tip_ids[0])
        dist_ring_thumb = self.calculate_distance(self.tip_ids[3], self.tip_ids[0])
        
        if debug_logging:
            print(f"[GetGestures] Distances: Index-Thumb={dist_index_thumb:.2f}, Middle-Thumb={dist_middle_thumb:.2f}, Ring-Thumb={dist_ring_thumb:.2f} (Threshold: {click_threshold_distance:.2f})")

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

        if debug_logging:
            print(f"[GetGestures] Pinch detected: {pinch_detected_this_frame}. Gestures after pinch: {gestures}")

        if not pinch_detected_this_frame:
            fingers_status = self.fingers_up(debug_logging=debug_logging) # Pass debug flag
            
            # Scroll Up: Current logic: [True, True, True, False, False]
            if fingers_status == [True, True, True, False, False]:
                gestures["scroll_up"] = True
            
            # Scroll Down: Current logic: [False, True, True, True, False]
            elif fingers_status == [False, True, True, True, False]: # Corrected based on original code
                gestures["scroll_down"] = True
        
        if debug_logging:
            print(f"[GetGestures] Final gestures: {gestures}")
        return gestures

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