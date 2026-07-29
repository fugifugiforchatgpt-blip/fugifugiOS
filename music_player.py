import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyglet
import os
import threading
import time
from mutagen.mp3 import MP3

class MusicPlayer:
    def __init__(self, parent, taskbar, filepath=None):
        self.parent = parent
        self.taskbar = taskbar
        self.current_file = None
        self.is_playing = False
        self.paused = False
        self.player = None
        self.total_length = 0
        self.update_thread = None
        self.stop_update = False

        self.create_window()

        if filepath and os.path.exists(filepath):
            self.load_file(filepath)
            self.play_music()

    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Музыкальный плеер")
        self.window.geometry("400x250")
        self.window.resizable(False, False)
        self.taskbar.add_window(self.window, "Музыкальный плеер")
        self.window.transient(self.parent)
        self.window.lift()
        self.window.focus_force()

        # Название трека
        title_frame = tk.Frame(self.window, bg="lightblue", height=80)
        title_frame.pack(fill=tk.X, padx=10, pady=5)

        self.song_title_label = tk.Label(title_frame, text="Нет трека", font=("Arial", 12, "bold"),
                                         bg="lightblue", wraplength=350, justify=tk.CENTER)
        self.song_title_label.pack(expand=True, fill=tk.BOTH)

        # Прогресс-бар
        progress_frame = tk.Frame(self.window)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        self.current_time_label = tk.Label(progress_frame, text="00:00", width=5)
        self.current_time_label.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.total_time_label = tk.Label(progress_frame, text="00:00", width=5)
        self.total_time_label.pack(side=tk.RIGHT)

        # Кнопки управления
        control_frame = tk.Frame(self.window)
        control_frame.pack(fill=tk.X, pady=10)

        self.play_pause_btn = tk.Button(control_frame, text="Воспроизвести", command=self.toggle_play_pause)
        self.play_pause_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(control_frame, text="Стоп", command=self.stop_music)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        # Регулировка громкости
        volume_frame = tk.Frame(self.window)
        volume_frame.pack(fill=tk.X, padx=10, pady=10)

        vol_label = tk.Label(volume_frame, text="Громкость:")
        vol_label.pack(side=tk.LEFT)

        self.volume_scroll = tk.Scale(volume_frame, from_=0, to=100, orient='horizontal', command=self.set_volume)
        self.volume_scroll.set(50)
        self.volume_scroll.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def load_file(self, filepath):
        self.current_file = filepath
        self.song_title_label.config(text=os.path.basename(filepath))
        try:
            audio = MP3(filepath)
            self.total_length = audio.info.length
            total_minutes = int(self.total_length // 60)
            total_seconds = int(self.total_length % 60)
            self.total_time_label.config(text=f"{total_minutes:02}:{total_seconds:02}")
            self.progress_bar['maximum'] = 100
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить метаданные MP3: {e}")

    def play_music(self):
        try:
            # Загружаем файл через pyglet
            self.player = pyglet.media.Player()
            source = pyglet.media.load(self.current_file)
            self.player.queue(source)
            self.player.volume = self.volume_scroll.get() / 100.0
            self.player.play()
            self.is_playing = True
            self.paused = False
            self.play_pause_btn.config(text="Пауза")
            self.start_update_thread()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести файл: {e}")

    def pause_music(self):
        if self.player:
            self.player.pause()
            self.paused = True
            self.is_playing = False
            self.play_pause_btn.config(text="Воспроизвести")

    def resume_music(self):
        if self.player:
            self.player.play()
            self.is_playing = True
            self.paused = False
            self.play_pause_btn.config(text="Пауза")
            self.start_update_thread()

    def toggle_play_pause(self):
        if self.current_file is None:
            return
        if not self.is_playing and not self.paused:
            self.play_music()
        elif self.is_playing and not self.paused:
            self.pause_music()
        elif not self.is_playing and self.paused:
            self.resume_music()

    def stop_music(self):
        self.stop_update = True
        if self.player:
            self.player.pause()
            self.player.seek(0)
        self.is_playing = False
        self.paused = False
        self.play_pause_btn.config(text="Воспроизвести")
        self.reset_ui()

    def set_volume(self, value):
        if self.player:
            self.player.volume = int(value) / 100.0

    def reset_ui(self):
        self.progress_bar['value'] = 0
        self.current_time_label.config(text="00:00")

    def update_progress(self):
        self.stop_update = False
        while not self.stop_update and self.is_playing and not self.paused:
            if self.player:
                try:
                    current_pos = self.player.time
                    if current_pos is not None and self.total_length > 0:
                        percent = (current_pos / self.total_length) * 100
                        self.progress_bar['value'] = percent
                        minutes = int(current_pos // 60)
                        seconds = int(current_pos % 60)
                        self.window.after(0, lambda m=minutes, s=seconds: self.current_time_label.config(text=f"{m:02}:{s:02}"))
                except:
                    pass
            time.sleep(0.1)
        if not self.stop_update and not self.paused:
            self.reset_ui()

    def start_update_thread(self):
        self.stop_update = True
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join()
        self.update_thread = threading.Thread(target=self.update_progress)
        self.stop_update = False
        self.update_thread.start()

    def on_close(self):
        self.stop_update = True
        if self.player:
            self.player.pause()
        self.taskbar.remove_window(self.window)
        self.window.destroy()