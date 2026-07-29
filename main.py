import tkinter as tk
from ff_bios import show_ff_bios
from loading import LoadingScreen
from desktop import show_desktop
from theme_utils import load_settings

def main():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.destroy())

    # Загружаем настройки
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