import tkinter as tk
from tkinter import ttk
import pyautogui
import time
import threading

# --- THEMES ---
THEMES = {
    "light": {
        "bg": "#f0f0f0",
        "key_bg": "#ffffff",
        "key_fg": "#000000",
        "hover_bg": "#e0e0e0",
        "special_key_bg": "#d0d0d0",
        "active_key_bg": "#a0a0a0",
    },
    "dark": {
        "bg": "#333333",
        "key_bg": "#555555",
        "key_fg": "#ffffff",
        "hover_bg": "#777777",
        "special_key_bg": "#444444",
        "active_key_bg": "#999999",
    }
}

# --- LAYOUTS ---
LAYOUTS = {
    "qwerty_en": [
        "` 1 2 3 4 5 6 7 8 9 0 - = {bksp}",
        "{tab} q w e r t y u i o p [ ] \",
        "{lock} a s d f g h j k l ; ' {enter}",
        "{shift} z x c v b n m , . / {shift_r}",
        "{space}"
    ]
}
LAYOUTS["qwerty_id"] = LAYOUTS["qwerty_en"] # Alias for now

class Key(tk.Button):
    def __init__(self, master, key_spec, keyboard_app, **kwargs):
        self.app = keyboard_app
        self.spec = key_spec
        self.char = key_spec["char"]
        self.action = key_spec["action"]
        
        super().__init__(master, text=self.char, **kwargs)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        
        self.is_hovered = False
        self.dwell_start_time = 0
        self.dwell_triggered = False

    def on_hover(self, event=None):
        self.is_hovered = True
        self.dwell_start_time = time.time()
        self.dwell_triggered = False
        self.app.set_hovered_key(self)
        self.update_style()

    def on_leave(self, event=None):
        self.is_hovered = False
        self.dwell_start_time = 0
        self.app.clear_hovered_key(self)
        self.update_style()

    def update_style(self, is_active=False):
        theme = self.app.theme
        
        bg = theme["key_bg"]
        if self.spec["type"] == "special":
            bg = theme["special_key_bg"]
        if is_active:
            bg = theme["active_key_bg"]
        if self.is_hovered:
            bg = theme["hover_bg"]
            
        self.config(background=bg, foreground=theme["key_fg"],
                    activebackground=theme["hover_bg"],
                    activeforeground=theme["key_fg"])

    def press(self):
        self.app.handle_key_press(self.action)
        # Visual feedback
        self.update_style(is_active=True)
        self.after(150, self.update_style)

class VirtualKeyboard(threading.Thread):
    def __init__(self, layout_name="qwerty_id", theme_name="light", dwell_time=0.7):
        super().__init__(daemon=True)
        self.layout_name = layout_name
        self.theme_name = theme_name
        self.dwell_time = dwell_time
        
        self.root = None
        self.keys = {}
        self.is_visible = False
        self.shift_active = False
        self.caps_lock_active = False
        
        self.hovered_key = None
        self.theme = THEMES.get(self.theme_name, THEMES["light"])
        
        self.ui_ready = threading.Event()

    def run(self):
        self.root = tk.Tk()
        self.root.title("Kursor Virtual Keyboard")
        self.root.wm_attributes("-topmost", 1)
        self.root.wm_attributes("-alpha", 0.9)
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self.root.withdraw() # Start hidden

        self.create_layout()
        self.ui_ready.set()
        self.root.mainloop()

    def create_layout(self):
        layout = LAYOUTS.get(self.layout_name, LAYOUTS["qwerty_en"])
        self.theme = THEMES.get(self.theme_name, THEMES["light"])
        
        self.root.config(bg=self.theme["bg"])
        
        for r, row_str in enumerate(layout):
            row_frame = tk.Frame(self.root, bg=self.theme["bg"])
            row_frame.grid(row=r, column=0, sticky="ew")
            
            for c, key_char in enumerate(row_str.split()):
                key_spec = self.parse_key_spec(key_char)
                
                key_widget = Key(row_frame, key_spec, self,
                                 font=("Segoe UI", 10),
                                 borderwidth=1, relief="raised",
                                 padx=10, pady=10)
                
                key_widget.grid(row=0, column=c, sticky="ew", padx=2, pady=2)
                row_frame.grid_columnconfigure(c, weight=key_spec["width"])
                
                self.keys[key_spec["action"]] = key_widget
        self.update_key_labels()

    def parse_key_spec(self, key_char):
        spec = {"type": "char", "width": 1}
        if key_char.startswith("{") and key_char.endswith("}"):
            action = key_char[1:-1]
            spec.update({"type": "special", "char": action.upper(), "action": action})
            if action in ["bksp", "enter", "tab"]:
                spec["width"] = 2
            elif action in ["lock", "shift", "shift_r"]:
                spec["width"] = 3
            elif action == "space":
                spec["width"] = 15
                spec["char"] = " "
        else:
            spec.update({"char": key_char, "action": key_char})
        return spec

    def update_key_labels(self):
        is_upper = self.shift_active or self.caps_lock_active
        for key in self.keys.values():
            if key.spec["type"] == "char":
                char = key.spec["char"]
                if len(char) == 1: # Avoid changing "Bksp", etc.
                    new_char = char.upper() if is_upper else char.lower()
                    key.config(text=new_char)
            key.update_style(is_active=(
                (key.action == "shift" and self.shift_active) or
                (key.action == "lock" and self.caps_lock_active)
            ))

    def handle_key_press(self, action):
        if action == "shift" or action == "shift_r":
            self.shift_active = not self.shift_active
            self.update_key_labels()
        elif action == "lock":
            self.caps_lock_active = not self.caps_lock_active
            self.update_key_labels()
        elif action == "bksp":
            pyautogui.press("backspace")
        elif action == "enter":
            pyautogui.press("enter")
        elif action == "tab":
            pyautogui.press("tab")
        elif action == "space":
            pyautogui.press("space")
        else: # Character key
            key_widget = self.keys.get(action)
            if key_widget:
                char_to_type = key_widget.cget("text")
                pyautogui.typewrite(char_to_type)
            if self.shift_active:
                self.shift_active = False
                self.update_key_labels()

    def set_hovered_key(self, key_widget):
        if self.hovered_key and self.hovered_key != key_widget:
            self.hovered_key.on_leave()
        self.hovered_key = key_widget

    def clear_hovered_key(self, key_widget):
        if self.hovered_key == key_widget:
            self.hovered_key = None
            
    def handle_input(self, pointer_x, pointer_y, click_event):
        if not self.is_visible:
            return None
            
        # Dwell clicking logic
        if self.hovered_key and self.hovered_key.is_hovered:
            if not self.hovered_key.dwell_triggered:
                if time.time() - self.hovered_key.dwell_start_time > self.dwell_time:
                    self.hovered_key.press()
                    self.hovered_key.dwell_triggered = True
        
        # Gesture clicking logic
        if click_event and self.hovered_key:
            self.hovered_key.press()
            
    def set_visibility(self, visible):
        if not self.is_alive():
            self.start()
            self.ui_ready.wait()

        if visible and not self.is_visible:
            self.is_visible = True
            self.root.deiconify()
        elif not visible and self.is_visible:
            self.is_visible = False
            self.root.withdraw()

    def show(self):
        self.set_visibility(True)

    def hide(self):
        self.set_visibility(False)

    def toggle(self):
        self.set_visibility(not self.is_visible)

if __name__ == '__main__':
    # Standalone test
    print("Starting virtual keyboard test...")
    keyboard = VirtualKeyboard(theme_name="dark")
    keyboard.show()

    # Simulate mouse movement for testing hover
    def move_mouse_over_keys():
        keyboard.ui_ready.wait() # Wait for tkinter to be ready
        
        print("UI is ready. Simulating mouse hover...")
        time.sleep(2)
        
        # Simulate hovering over a few keys
        keys_to_hover = ["q", "w", "e", "r", "t", "y"]
        for key_char in keys_to_hover:
            if keyboard.is_visible:
                key_widget = keyboard.keys.get(key_char)
                if key_widget:
                    x = key_widget.winfo_rootx() + key_widget.winfo_width() // 2
                    y = key_widget.winfo_rooty() + key_widget.winfo_height() // 2
                    pyautogui.moveTo(x, y, duration=0.2)
                    print(f"Hovering over '{key_char}'")
                    time.sleep(0.5)
        
        print("Simulating dwell click on 'a'...")
        key_a = keyboard.keys.get("a")
        if key_a:
            x = key_a.winfo_rootx() + key_a.winfo_width() // 2
            y = key_a.winfo_rooty() + key_a.winfo_height() // 2
            pyautogui.moveTo(x, y, duration=0.2)
            time.sleep(keyboard.dwell_time + 0.2) # Wait for dwell
            
        time.sleep(2)
        print("Hiding keyboard.")
        keyboard.hide()
        time.sleep(2)
        print("Showing keyboard.")
        keyboard.show()
        time.sleep(2)
        print("Test finished. Closing.")
        keyboard.root.quit()

    # Run mouse simulation in a separate thread
    mouse_sim_thread = threading.Thread(target=move_mouse_over_keys)
    mouse_sim_thread.daemon = True
    mouse_sim_thread.start()

    # The main thread will run the tkinter mainloop via keyboard.run()
    # Since keyboard is a daemon thread, we need to keep the main thread alive
    try:
        while keyboard.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting.")
        if keyboard.root:
            keyboard.root.quit()