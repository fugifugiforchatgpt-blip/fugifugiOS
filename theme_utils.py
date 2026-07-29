# theme_utils.py
import json
import os

SETTINGS_FILE = "settings.json"

# Неоновые цветовые схемы
NEON_COLORS = {
    "Розовый": {
        "bg": "#0a0a1a",
        "fg": "#ff00ff",
        "accent": "#ff66ff",
        "glow": "#ff00ff",
        "button": "#cc00cc",
        "taskbar": "#0d0d2b",
        "border": "#ff44ff"
    },
    "Голубой": {
        "bg": "#0a0a1a",
        "fg": "#00ffff",
        "accent": "#66ffff",
        "glow": "#00ffff",
        "button": "#0099cc",
        "taskbar": "#0d1a2b",
        "border": "#44ddff"
    },
    "Фиолетовый": {
        "bg": "#0a0a1a",
        "fg": "#aa44ff",
        "accent": "#cc88ff",
        "glow": "#aa44ff",
        "button": "#7722bb",
        "taskbar": "#150a2b",
        "border": "#bb66ff"
    },
    "Зелёный": {
        "bg": "#0a0a1a",
        "fg": "#00ff44",
        "accent": "#66ff88",
        "glow": "#00ff44",
        "button": "#00bb33",
        "taskbar": "#0a1a0d",
        "border": "#44ff66"
    },
    "Оранжевый": {
        "bg": "#0a0a1a",
        "fg": "#ff6600",
        "accent": "#ff9933",
        "glow": "#ff6600",
        "button": "#cc5500",
        "taskbar": "#1a0d0a",
        "border": "#ff8833"
    }
}

def init_settings():
    if not os.path.exists(SETTINGS_FILE):
        default = {
            "bg_color": "lightblue",
            "theme": "light",
            "neon_mode": False,
            "neon_color": "Розовый"
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default, f)

def load_settings():
    default = {
        "bg_color": "lightblue",
        "theme": "light",
        "neon_mode": False,
        "neon_color": "Розовый"
    }
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default, f)
        return default
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            for key in default:
                if key not in data:
                    data[key] = default[key]
            return data
    except:
        return default

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_theme():
    return load_settings().get("theme", "light")

def set_theme(theme):
    data = load_settings()
    data["theme"] = theme
    save_settings(data)

def get_bg_color():
    return load_settings().get("bg_color", "lightblue")

def get_neon_theme(color_name):
    return NEON_COLORS.get(color_name, NEON_COLORS["Розовый"])

def is_neon_mode():
    return load_settings().get("neon_mode", False)