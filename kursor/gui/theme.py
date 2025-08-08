
import tkinter as tk
from tkinter import ttk

def apply_theme(root):
    style = ttk.Style(root)

    # Define warm color palette
    bg_color = "#FDF5E6"  # Old Lace
    primary_color = "#E6A47E"  # Burnt Sienna
    secondary_color = "#F4DDBE"  # Champagne Pink
    text_color = "#5D4037"  # Dark Brown
    accent_color = "#FF7043"  # Coral

    # Configure the theme
    style.theme_create("warm_theme", parent="alt", settings={
        ".": {
            "configure": {
                "background": bg_color,
                "foreground": text_color,
                "font": ("Helvetica", 10)
            }
        },
        "TButton": {
            "configure": {
                "background": primary_color,
                "foreground": "white",
                "padding": 5,
                "font": ("Helvetica", 10, "bold"),
                "borderwidth": 0,
                "relief": tk.FLAT
            },
            "map": {
                "background": [("active", accent_color)],
            }
        },
        "TNotebook": {
            "configure": {
                "background": bg_color,
                "tabmargins": [2, 5, 2, 0],
            }
        },
        "TNotebook.Tab": {
            "configure": {
                "padding": [10, 5],
                "background": secondary_color,
                "foreground": text_color,
                "font": ("Helvetica", 10, "bold")
            },
            "map": {
                "background": [("selected", primary_color)],
                "expand": [("selected", [1, 1, 1, 0])]
            }
        },
        "TFrame": {
            "configure": {
                "background": bg_color
            }
        },
        "TLabel": {
            "configure": {
                "background": bg_color,
                "foreground": text_color
            }
        },
        "TLabelFrame": {
            "configure": {
                "background": bg_color,
                "foreground": text_color,
                "font": ("Helvetica", 11, "bold"),
                "relief": tk.GROOVE,
                "borderwidth": 1
            }
        },
        "TScale": {
            "configure": {
                "background": primary_color
            }
        }
    })

    style.theme_use("warm_theme")

