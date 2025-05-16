import pyautogui
import numpy as np

class MouseHandler:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.prev_x, self.prev_y = 0, 0
        self.smoothing_factor = 0.3 # Semakin kecil semakin halus tapi lambat, 0.1 - 0.5 adalah rentang baik
        
        # Nonaktifkan failsafe jika Anda yakin, tapi berhati-hati
        # pyautogui.FAILSAFE = False 

    def move_mouse(self, cam_x, cam_y, cam_width, cam_height, active_region_padding_percent=0.15):
        if cam_x == -1 or cam_y == -1: # Jika landmark tidak terdeteksi
            return

        # Tentukan area aktif di kamera untuk menghindari gerakan dari tepi
        padding_x = int(cam_width * active_region_padding_percent)
        padding_y = int(cam_height * active_region_padding_percent)
        
        active_cam_width = cam_width - 2 * padding_x
        active_cam_height = cam_height - 2 * padding_y

        # Pastikan cam_x dan cam_y berada dalam batas area aktif (setelah padding)
        # dan normalisasi ulang ke rentang [0, active_cam_width/height]
        norm_x = np.clip(cam_x - padding_x, 0, active_cam_width)
        norm_y = np.clip(cam_y - padding_y, 0, active_cam_height)

        # Interpolasi koordinat kamera ke koordinat layar
        # Ingat untuk membalik sumbu X kamera karena efek cermin
        screen_x = np.interp(norm_x, [0, active_cam_width], [self.screen_width, 0]) 
        screen_y = np.interp(norm_y, [0, active_cam_height], [0, self.screen_height])

        # Smoothing
        current_x = self.prev_x + (screen_x - self.prev_x) * self.smoothing_factor
        current_y = self.prev_y + (screen_y - self.prev_y) * self.smoothing_factor

        # Batasi pergerakan mouse agar tidak keluar layar (penting!)
        current_x = np.clip(current_x, 0, self.screen_width -1) # -1 agar tidak error di batas
        current_y = np.clip(current_y, 0, self.screen_height -1)

        pyautogui.moveTo(int(current_x), int(current_y))
        
        self.prev_x = current_x
        self.prev_y = current_y

    def perform_click(self, click_type="left"):
        if click_type == "left":
            pyautogui.click(button='left')
            print("Klik Kiri Dilakukan")
        elif click_type == "right":
            pyautogui.click(button='right')
            print("Klik Kanan Dilakukan")