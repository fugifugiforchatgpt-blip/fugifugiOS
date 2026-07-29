# utils.py
import tkinter as tk

def set_fullscreen(window):
    """Переводит окно в полноэкранный режим"""
    window.attributes("-fullscreen", True)
    window.bind("<Escape>", lambda e: window.attributes("-fullscreen", False))

def center_window(window, width, height):
    """Центрирует окно на экране (если не полноэкранный режим)"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def unset_fullscreen(window):
    window.attributes("-fullscreen", False)