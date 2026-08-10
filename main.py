# main.py
import tkinter as tk
from ff_bios import show_ff_bios
from loading import LoadingScreen
from desktop import show_desktop
from theme_utils import load_settings
from drivers import get_driver_manager  # <-- НОВЫЙ ИМПОРТ

def main():
    # ============================================
    # 1. ИНИЦИАЛИЗАЦИЯ ДРАЙВЕРОВ ПРИ СТАРТЕ
    # ============================================
    # Создаём (или получаем) единый экземпляр менеджера драйверов
    driver_manager = get_driver_manager()
    
    # Загружаем настройки из файла
    settings = load_settings()
    driver_settings = settings.get("drivers", {})
    
    # Применяем сохранённые драйверы (если есть)
    for device_type, driver_name in driver_settings.items():
        if driver_manager.set_driver(device_type, driver_name):
            print(f"[Драйверы] Загружен {device_type} -> {driver_name}")
        else:
            print(f"[Драйверы] Ошибка: {device_type} -> {driver_name} не найден")
    
    # Если драйверы не сохранены, устанавливаем стандартные
    if not driver_settings:
        driver_manager.set_driver("mouse", "standart")
        driver_manager.set_driver("keyboard", "standart")
        driver_manager.set_driver("joystick", "standart")
        print("[Драйверы] Установлены стандартные драйверы")
    
    # ============================================
    # 2. ЗАПУСК ГРАФИЧЕСКОГО ИНТЕРФЕЙСА
    # ============================================
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.destroy())
    
    # Загружаем настройки (повторно, для BIOS и прочего)
    settings = load_settings()
    skip_bios = settings.get("skip_bios", False)
    
    def after_bios(master):
        LoadingScreen(master, lambda master2: show_desktop(master2))
    
    if skip_bios:
        # Сразу показываем экран загрузки (или рабочий стол без BIOS)
        LoadingScreen(root, lambda master: show_desktop(master))
    else:
        show_ff_bios(root, after_bios)
    
    root.mainloop()

if __name__ == "__main__":
    main()