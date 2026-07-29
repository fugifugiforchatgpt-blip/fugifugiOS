# ff_bios.py
import tkinter as tk
import os
import json
import platform
import subprocess
import sys

# Пытаемся импортировать psutil (если нет, выведем базовую информацию)
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil не установлен, информация о железе будет неполной")


def get_cpu_name():
    """Возвращает название процессора и количество ядер"""
    if platform.system() == "Windows":
        try:
            # Через реестр (работает на всех Windows)
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
            winreg.CloseKey(key)
            return cpu_name.strip()
        except:
            pass
    # fallback
    cpu = platform.processor()
    if not cpu or cpu == "Intel64 Family 6 Model 158 Stepping 13":
        # Если пусто, пробуем другой метод
        if platform.system() == "Windows":
            try:
                output = subprocess.check_output("wmic cpu get name", shell=True, text=True, encoding='cp866')
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    cpu = lines[1].strip()
            except:
                pass
    return cpu or "Неизвестный процессор"


def get_ram_gb():
    """Возвращает объём ОЗУ в ГБ (округлённо)"""
    if PSUTIL_AVAILABLE:
        total = psutil.virtual_memory().total
        return round(total / (1024 ** 3), 1)
    # fallback для Windows через ctypes
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        memoryStatus = MEMORYSTATUSEX()
        memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
        total = memoryStatus.ullTotalPhys
        return round(total / (1024 ** 3), 1)
    except:
        return "?"


def get_gpu_name():
    """Возвращает название видеокарты (Windows через wmic)"""
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output("wmic path win32_VideoController get name", shell=True, text=True,
                                             encoding='cp866')
            lines = output.strip().split('\n')
            # Ищем первую непустую строку после заголовка
            for line in lines[1:]:
                line = line.strip()
                if line and line != "Name" and not line.startswith("Microsoft"):
                    # Ограничим длину
                    if len(line) > 40:
                        line = line[:37] + "..."
                    return line
        except:
            pass
    return "Видеокарта (не определена)"


def get_disk_info():
    """Возвращает список дисков и их размеров"""
    disks = []
    if PSUTIL_AVAILABLE:
        for part in psutil.disk_partitions():
            if 'cdrom' in part.opts or part.fstype == '':
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                size_gb = usage.total / (1024 ** 3)
                disks.append(f"{part.device} ({part.mountpoint}) - {size_gb:.1f} GB")
            except:
                pass
    else:
        # fallback для Windows
        import ctypes
        drives = []
        drivebits = ctypes.cdll.kernel32.GetLogicalDrives()
        for i in range(26):
            if drivebits & (1 << i):
                drive_letter = chr(65 + i) + ":\\"
                drives.append(drive_letter)
        for drive in drives:
            try:
                import shutil
                total, used, free = shutil.disk_usage(drive)
                size_gb = total / (1024 ** 3)
                disks.append(f"{drive} - {size_gb:.1f} GB")
            except:
                pass
    return disks


def get_network_interfaces():
    """Возвращает имена сетевых карт"""
    if PSUTIL_AVAILABLE:
        interfaces = list(psutil.net_if_stats().keys())
        return interfaces[:3]  # первые три
    return ["Ethernet", "Wi-Fi"]


def ensure_environment(text_area, update_callback):
    """Создаёт папки и JSON-файлы, как раньше"""
    if not os.path.exists("files"):
        os.makedirs("files")
        update_callback("files: папка создана")
    else:
        update_callback("files: папка найдена")

    if not os.path.exists("settings.json"):
        default = {"bg_color": "lightblue"}
        with open("settings.json", "w") as f:
            json.dump(default, f)
        update_callback("settings.json: создан (цвет по умолчанию)")
    else:
        update_callback("settings.json: найден")

    if not os.path.exists("session.json"):
        with open("session.json", "w") as f:
            json.dump([], f)
        update_callback("session.json: создан (пустой)")
    else:
        update_callback("session.json: найден")


def show_ff_bios(master, on_complete):
    for widget in master.winfo_children():
        widget.destroy()
    master.configure(bg="black")
    master.attributes("-fullscreen", True)
    master.title("Fugi_fugi BIOS - Real Hardware Detection")

    text_area = tk.Text(master, bg="black", fg="lime", font=("Courier", 14), wrap=tk.WORD, state='normal')
    text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    text_area.config(state='disabled')

    def update_display(msg):
        text_area.config(state='normal')
        text_area.insert(tk.END, msg + "\n")
        text_area.see(tk.END)
        text_area.config(state='disabled')
        master.update()

    # Заголовок
    messages = [
        "Fugi_fugi BIOS (c) 2026 Fugi_fugi Corp.",
        "",
        "POST (Power-On Self-Test) v3.0 - Real Hardware Detection",
        "",
        f"CPU: {get_cpu_name()} ({os.cpu_count()} ядер, логических процессоров: {os.cpu_count()})",
        f"RAM: {get_ram_gb()} GB",
    ]

    # Видеокарта
    gpu = get_gpu_name()
    messages.append(f"GPU: {gpu}")

    # Диски
    disks = get_disk_info()
    for disk in disks:
        messages.append(f"Диск: {disk}")

    # Сеть
    net_ifaces = get_network_interfaces()
    messages.append(f"Сетевые интерфейсы: {', '.join(net_ifaces)}")

    # Аудио (упрощённо)
    messages.append("Аудио: Realtek HD Audio (предположительно)")
    messages.append("Secure Boot: Выключен (ФФ режим)")
    messages.append("")
    messages.append("Проверка системных файлов:")

    def display_messages(idx=0):
        if idx < len(messages):
            update_display(messages[idx])
            # Скорость вывода: первые быстро, потом чуть медленнее
            delay = 600 if idx < 5 else 400 if idx < 15 else 300
            master.after(delay, lambda: display_messages(idx + 1))
        else:
            # Проверка/создание окружения
            ensure_environment(text_area, update_display)
            master.after(1000, lambda: on_complete(master))

    display_messages()