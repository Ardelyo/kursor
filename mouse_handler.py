

import pyautogui
import numpy as np
import time

class MouseHandler:
    def __init__(self, screen_width, screen_height, default_scroll=100): # Tambahkan default_scroll
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.prev_x, self.prev_y = 0, 0
        self.smoothing_factor = 0.3 
        pyautogui.FAILSAFE = True
        self.is_dragging = False
        self.last_action_time = {} # Dictionary untuk cooldown per tipe aksi
        self.action_cooldown_map = { # Default cooldowns
            "default": 0.3, 
            "scroll": 0.1,
            "left_click": 0.2, # Bisa disesuaikan lebih lanjut
            "right_click": 0.2,
            "double_click": 0.3,
            "drag_toggle": 0.3
        }
        self.default_scroll_amount = default_scroll # Simpan default scroll

    def set_action_cooldowns(self, default=None, scroll=None, left_click=None, right_click=None, double_click=None, drag_toggle=None):
        """Mengatur cooldown untuk berbagai jenis aksi."""
        if default is not None: self.action_cooldown_map["default"] = default
        if scroll is not None: self.action_cooldown_map["scroll"] = scroll
        if left_click is not None: self.action_cooldown_map["left_click"] = left_click
        if right_click is not None: self.action_cooldown_map["right_click"] = right_click
        if double_click is not None: self.action_cooldown_map["double_click"] = double_click
        if drag_toggle is not None: self.action_cooldown_map["drag_toggle"] = drag_toggle
        # Pastikan semua action type punya entry di last_action_time
        for action_type in self.action_cooldown_map.keys():
            if action_type not in self.last_action_time:
                self.last_action_time[action_type] = 0


    def _can_perform_action(self, action_type="default"):
        """Memeriksa apakah aksi dapat dilakukan berdasarkan cooldown."""
        cooldown = self.action_cooldown_map.get(action_type, self.action_cooldown_map["default"])
        current_time = time.time()
        
        # Inisialisasi last_action_time jika belum ada untuk tipe aksi ini
        if action_type not in self.last_action_time:
            self.last_action_time[action_type] = 0
            
        can_act = (current_time - self.last_action_time.get(action_type, 0)) > cooldown
        if can_act:
            self.last_action_time[action_type] = current_time
        # else: # Debugging cooldown
            # print(f"Cooldown active for {action_type}: {(current_time - self.last_action_time.get(action_type, 0)):.2f}s <= {cooldown:.2f}s")
        return can_act

    def move_mouse(self, cam_x, cam_y, cam_width, cam_height, active_region_padding_percent=0.15):
        if cam_x == -1 or cam_y == -1:
            return

        padding_x = int(cam_width * active_region_padding_percent)
        padding_y = int(cam_height * active_region_padding_percent)
        
        active_cam_width = cam_width - 2 * padding_x
        active_cam_height = cam_height - 2 * padding_y

        if active_cam_width <= 0 : active_cam_width = 1 
        if active_cam_height <= 0 : active_cam_height = 1

        norm_x = np.clip(cam_x - padding_x, 0, active_cam_width)
        norm_y = np.clip(cam_y - padding_y, 0, active_cam_height)

        screen_x = np.interp(norm_x, [0, active_cam_width], [0, self.screen_width]) 
        screen_y = np.interp(norm_y, [0, active_cam_height], [0, self.screen_height])

        current_x = self.prev_x + (screen_x - self.prev_x) * self.smoothing_factor
        current_y = self.prev_y + (screen_y - self.prev_y) * self.smoothing_factor

        current_x = np.clip(current_x, 0, self.screen_width -1)
        current_y = np.clip(current_y, 0, self.screen_height -1)

        if self.is_dragging:
            pyautogui.dragTo(int(current_x), int(current_y), button='left', duration=0)
        else:
            pyautogui.moveTo(int(current_x), int(current_y), duration=0)
        
        self.prev_x = current_x
        self.prev_y = current_y

    def left_click(self):
        if self._can_perform_action("left_click"):
            pyautogui.click(button='left')
            print("Klik Kiri")
            return True
        return False

    def right_click(self):
        if self._can_perform_action("right_click"):
            pyautogui.click(button='right')
            print("Klik Kanan")
            return True
        return False
            
    def double_click(self):
        if self._can_perform_action("double_click"):
            pyautogui.doubleClick()
            print("Double Klik")
            return True
        return False

    def toggle_drag(self):
        if self._can_perform_action("drag_toggle"):
            self.is_dragging = not self.is_dragging
            if self.is_dragging:
                pyautogui.mouseDown(button='left')
                print("Mode Drag: AKTIF")
            else:
                pyautogui.mouseUp(button='left')
                print("Mode Drag: NONAKTIF")
            return True
        return False

    def scroll(self, amount):
        if self._can_perform_action("scroll"):
            pyautogui.scroll(amount)
            direction = "Atas" if amount > 0 else "Bawah"
            print(f"Scroll {direction} ({amount})")
            return True
        return False