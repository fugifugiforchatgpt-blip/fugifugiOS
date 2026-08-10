# -*- coding: utf-8 -*-
"""
Драйверы для FugiFugi OS (v0.2)
Все драйверы собраны в одном файле.
Каждый драйвер — это функция, которая принимает сырые данные и возвращает обработанные.
Менеджер драйверов позволяет выбирать, какой драйвер использовать для каждого устройства.
"""

import time
import random
import math
from typing import Any, Dict, Callable, Optional

# ================================================
#  КЛАСС МЕНЕДЖЕР ДРАЙВЕРОВ
# ================================================

class DriverManager:
    """
    Управляет выбором драйверов для устройств.
    Хранит соответствие: устройство → имя драйвера.
    Позволяет переключать драйверы на лету.
    """
    def __init__(self):
        # Словарь настроек: какой драйвер выбран для каждого устройства
        self.settings: Dict[str, str] = {
            "mouse": "standart",
            "keyboard": "standart",
            "joystick": "standart",
        }
        
        # Словарь доступных драйверов для каждого устройства
        self.available_drivers: Dict[str, Dict[str, Callable]] = {
            "mouse": {
                "standart": self.mouse_standart,
                "gaming": self.mouse_gaming,
                "precision": self.mouse_precision,
                "analyst": self.mouse_analyst,
            },
            "keyboard": {
                "standart": self.keyboard_standart,
                "macro": self.keyboard_macro,
                "translator": self.keyboard_translator,
                "gamer": self.keyboard_gamer,
            },
            "joystick": {
                "standart": self.joystick_standart,
                "racing": self.joystick_racing,
                "space": self.joystick_space,
            }
        }
        
        # Словарь для хранения истории (для аналитики)
        self.history: Dict[str, list] = {
            "mouse": [],
            "keyboard": [],
            "joystick": []
        }

    # ================================================
    #  ДРАЙВЕРЫ МЫШИ
    # ================================================

    def mouse_standart(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Стандартный драйвер мыши.
        Передаёт координаты как есть, без изменений.
        raw_data: {"x": int, "y": int, "buttons": int}
        """
        return {
            "x": raw_data.get("x", 0),
            "y": raw_data.get("y", 0),
            "buttons": raw_data.get("buttons", 0),
            "dx": raw_data.get("dx", 0),
            "dy": raw_data.get("dy", 0),
        }

    def mouse_gaming(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Игровой драйвер мыши.
        Увеличивает чувствительность в 2 раза, добавляет небольшое сглаживание.
        """
        x = raw_data.get("x", 0)
        y = raw_data.get("y", 0)
        return {
            "x": int(x * 2),
            "y": int(y * 2),
            "buttons": raw_data.get("buttons", 0),
            "dx": raw_data.get("dx", 0) * 2,
            "dy": raw_data.get("dy", 0) * 2,
        }

    def mouse_precision(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Точный драйвер (для рисования).
        Замедляет движение, убирает дрожание через усреднение.
        """
        hist = self.history["mouse"]
        hist.append((raw_data.get("x", 0), raw_data.get("y", 0)))
        if len(hist) > 3:
            hist.pop(0)
        if len(hist) == 3:
            avg_x = int(sum(p[0] for p in hist) / 3)
            avg_y = int(sum(p[1] for p in hist) / 3)
        else:
            avg_x = raw_data.get("x", 0)
            avg_y = raw_data.get("y", 0)
        return {
            "x": avg_x,
            "y": avg_y,
            "buttons": raw_data.get("buttons", 0),
            "dx": raw_data.get("dx", 0) // 2,
            "dy": raw_data.get("dy", 0) // 2,
        }

    def mouse_analyst(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Аналитик – вместо перемещения выводит график движения.
        """
        hist = self.history["mouse"]
        hist.append((raw_data.get("x", 0), raw_data.get("y", 0), time.time()))
        if len(hist) > 100:
            hist.pop(0)
        return {
            "x": raw_data.get("x", 0),
            "y": raw_data.get("y", 0),
            "buttons": raw_data.get("buttons", 0),
            "analytics": True,
            "history_size": len(hist),
        }

    # ================================================
    #  ДРАЙВЕРЫ КЛАВИАТУРЫ
    # ================================================

    def keyboard_standart(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Стандартный драйвер клавиатуры.
        """
        return {
            "key": raw_data.get("key", ""),
            "modifiers": raw_data.get("modifiers", 0),
            "pressed": raw_data.get("pressed", False),
        }

    def keyboard_macro(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Макро-драйвер: заменяет комбинации клавиш.
        """
        key = raw_data.get("key", "")
        pressed = raw_data.get("pressed", False)
        if pressed:
            if key == "F1":
                return {"key": "s", "modifiers": 3, "pressed": True}
            elif key == "F2":
                return {"key": "c", "modifiers": 2, "pressed": True}
        return raw_data

    def keyboard_translator(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Переводчик раскладки на лету (QWERTY → Dvorak)
        """
        key = raw_data.get("key", "")
        qwerty_to_dvorak = {
            "q": "'", "w": ",", "e": ".", "r": "p", "t": "y",
            "y": "f", "u": "g", "i": "c", "o": "r", "p": "l",
        }
        if key in qwerty_to_dvorak:
            return {"key": qwerty_to_dvorak[key], "modifiers": raw_data.get("modifiers", 0), "pressed": raw_data.get("pressed", False)}
        return raw_data

    def keyboard_gamer(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Геймерский драйвер: блокирует Windows-клавишу.
        """
        key = raw_data.get("key", "")
        if key in ("Lwin", "Rwin"):
            return None
        return raw_data

    # ================================================
    #  ДРАЙВЕРЫ ДЖОЙСТИКА
    # ================================================

    def joystick_standart(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "x": raw_data.get("x", 0.0),
            "y": raw_data.get("y", 0.0),
            "z": raw_data.get("z", 0.0),
            "buttons": raw_data.get("buttons", []),
        }

    def joystick_racing(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        x = raw_data.get("x", 0.0)
        x_new = x * abs(x) * 1.2
        if x_new > 1.0: x_new = 1.0
        if x_new < -1.0: x_new = -1.0
        return {
            "x": x_new,
            "y": raw_data.get("y", 0.0),
            "z": raw_data.get("z", 0.0),
            "buttons": raw_data.get("buttons", []),
        }

    def joystick_space(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "roll": raw_data.get("x", 0.0),
            "pitch": raw_data.get("y", 0.0),
            "yaw": raw_data.get("z", 0.0),
            "buttons": raw_data.get("buttons", []),
        }

    # ================================================
    #  ОБЩАЯ ФУНКЦИЯ ОБРАБОТКИ
    # ================================================

    def process_input(self, device_type: str, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if device_type not in self.settings:
            return raw_data
        driver_name = self.settings[device_type]
        available = self.available_drivers.get(device_type, {})
        if driver_name not in available:
            return raw_data
        driver_func = available[driver_name]
        try:
            return driver_func(raw_data)
        except Exception as e:
            print(f"Ошибка в драйвере {device_type}::{driver_name}: {e}")
            return raw_data

    def set_driver(self, device_type: str, driver_name: str) -> bool:
        if device_type not in self.available_drivers:
            return False
        if driver_name not in self.available_drivers[device_type]:
            return False
        self.settings[device_type] = driver_name
        return True

    def get_drivers_list(self, device_type: str) -> list:
        return list(self.available_drivers.get(device_type, {}).keys())

    def test(self):
        print("=== ТЕСТ ДРАЙВЕРОВ ===")
        raw = {"x": 100, "y": 50, "buttons": 1, "dx": 10, "dy": 5}
        print("\nМЫШЬ:")
        for name in self.get_drivers_list("mouse"):
            self.set_driver("mouse", name)
            print(f"  {name}: {self.process_input('mouse', raw)}")
        raw = {"key": "F1", "modifiers": 0, "pressed": True}
        print("\nКЛАВИАТУРА:")
        for name in self.get_drivers_list("keyboard"):
            self.set_driver("keyboard", name)
            print(f"  {name}: {self.process_input('keyboard', raw)}")
        self.set_driver("mouse", "standart")

# ================================================
#  СИНГЛТОН (единый экземпляр для всей ОС)
# ================================================

_manager = None

def get_driver_manager() -> DriverManager:
    global _manager
    if _manager is None:
        _manager = DriverManager()
    return _manager

# ================================================
#  ТЕСТ ПРИ ЗАПУСКЕ
# ================================================

if __name__ == "__main__":
    manager = get_driver_manager()
    manager.test()