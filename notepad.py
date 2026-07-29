import tkinter as tk
import os


class Notepad:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar
        self.filename = "notes.txt"
        self.window = tk.Toplevel(parent)
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()
        self.window.title("Блокнот")
        self.window.geometry("500x400")
        taskbar.add_window(self.window, "Блокнот")

        self.text_area = tk.Text(self.window, wrap="word", font=("Consolas", 12))
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)
        self.load_text()

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill="x", padx=5, pady=5)
        tk.Button(btn_frame, text="Сохранить", command=self.save_text).pack(side="left", padx=5)

    def load_text(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.text_area.insert("1.0", f.read())
            except:
                pass

    def save_text(self):
        content = self.text_area.get("1.0", tk.END).rstrip("\n")
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(content)
        except:
            pass