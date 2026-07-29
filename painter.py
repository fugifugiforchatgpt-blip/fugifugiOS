import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageTk
import os

class Painter:
    def __init__(self, parent, taskbar, filepath=None):
        self.parent = parent
        self.taskbar = taskbar
        self.filepath = filepath
        self.brush_color = "black"
        self.brush_size = 5
        self.last_x = None
        self.last_y = None
        self.eraser_mode = False

        self.window = tk.Toplevel(parent)
        title = "Рисовалка" + (f" - {os.path.basename(filepath)}" if filepath else " - Новый рисунок")
        self.window.title(title)
        self.window.geometry("800x600")
        self.taskbar.add_window(self.window, title)
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()

        self.canvas = tk.Canvas(self.window, bg="white", cursor="pencil")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tool_frame = tk.Frame(self.window)
        tool_frame.pack(fill=tk.X, padx=5, pady=5)

        self.color_btn = tk.Button(tool_frame, text="Цвет", command=self.choose_color, bg=self.brush_color)
        self.color_btn.pack(side=tk.LEFT, padx=2)

        self.eraser_btn = tk.Button(tool_frame, text="Ластик", command=self.toggle_eraser)
        self.eraser_btn.pack(side=tk.LEFT, padx=2)

        tk.Label(tool_frame, text="Толщина:").pack(side=tk.LEFT, padx=(10,2))
        self.size_slider = tk.Scale(tool_frame, from_=1, to=20, orient=tk.HORIZONTAL, command=self.change_size)
        self.size_slider.set(self.brush_size)
        self.size_slider.pack(side=tk.LEFT, padx=2)

        self.clear_btn = tk.Button(tool_frame, text="Очистить", command=self.clear_canvas)
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        self.save_btn = tk.Button(tool_frame, text="Сохранить", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=2)

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.img = Image.new("RGB", (800, 600), "white")
        self.draw_engine = ImageDraw.Draw(self.img)

        if filepath and os.path.exists(filepath):
            self.load_image(filepath)

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет", parent=self.window)
        if color_code and color_code[1]:
            self.brush_color = color_code[1]
            self.eraser_mode = False
            self.color_btn.config(bg=self.brush_color)

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode
        if self.eraser_mode:
            self.eraser_btn.config(relief=tk.SUNKEN, text="Ластик (вкл)")
        else:
            self.eraser_btn.config(relief=tk.RAISED, text="Ластик")

    def change_size(self, val):
        self.brush_size = int(val)

    def paint(self, event):
        x, y = event.x, event.y
        if self.last_x and self.last_y:
            color = "white" if self.eraser_mode else self.brush_color
            self.canvas.create_line(self.last_x, self.last_y, x, y,
                                    width=self.brush_size, fill=color, capstyle=tk.ROUND, smooth=True)
            self.draw_engine.line([self.last_x, self.last_y, x, y],
                                  fill=color, width=self.brush_size)
        self.last_x = x
        self.last_y = y

    def reset(self, event):
        self.last_x = None
        self.last_y = None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.img = Image.new("RGB", (800, 600), "white")
        self.draw_engine = ImageDraw.Draw(self.img)

    def load_image(self, filepath):
        try:
            self.img = Image.open(filepath).convert("RGB")
            self.draw_engine = ImageDraw.Draw(self.img)
            photo = ImageTk.PhotoImage(self.img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

    def save_image(self):
        # ИСПРАВЛЕНО: добавил parent=self.window
        if not self.filepath:
            name = simpledialog.askstring("Сохранить рисунок", "Введите имя файла (без расширения):", parent=self.window)
            if not name:
                return
            filename = name.strip().replace(" ", "_") + ".png"
            self.filepath = os.path.join("files", filename)
        try:
            self.img.save(self.filepath)
            messagebox.showinfo("Сохранено", f"Рисунок сохранён как {os.path.basename(self.filepath)}")
            self.taskbar.remove_window(self.window)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_close(self):
        temp_path = os.path.join("temp", "painter_autosave.png")
        self.img.save(temp_path)
        self.taskbar.remove_window(self.window)
        self.window.destroy()