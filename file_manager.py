import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import os
import shutil
from notepad import Notepad
from painter import Painter
from music_player import MusicPlayer

class FileManager:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar
        self.root_folder = "files"
        self.current_path = self.root_folder
        self.ensure_root_folder()

        self.clipboard = None

        self.window = tk.Toplevel(parent)
        self.window.title("Файловый менеджер")
        self.window.geometry("650x500")
        self.taskbar.add_window(self.window, "Файловый менеджер")
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()

        nav_frame = tk.Frame(self.window)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)

        self.back_btn = tk.Button(nav_frame, text="◀ Назад", command=self.go_back)
        self.back_btn.pack(side=tk.LEFT, padx=5)

        self.path_label = tk.Label(nav_frame, text=self.current_path, font=("Arial", 9), relief=tk.SUNKEN, anchor=tk.W)
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="Открыть", command=self.open_selected).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Удалить", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Новая папка", command=self.new_folder).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Новый текст", command=self.new_text_file).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Создать рисунок", command=self.new_picture).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Загрузить музыку", command=self.upload_music).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Обновить", command=self.refresh).pack(side=tk.LEFT, padx=2)

        self.listbox = tk.Listbox(self.window, font=("Consolas", 12))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_selected())
        self.listbox.bind("<Button-3>", self.show_context_menu)

        self.refresh()

    def ensure_root_folder(self):
        if not os.path.exists(self.root_folder):
            os.makedirs(self.root_folder)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.path_label.config(text=self.current_path)
        try:
            items = sorted(os.listdir(self.current_path))
            for item in items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    display = f"📁 {item}"
                else:
                    ext = os.path.splitext(item)[1].lower()
                    if ext == ".txt":
                        display = f"📄 {item}"
                    elif ext == ".png":
                        display = f"🖼️ {item}"
                    elif ext == ".mp3":
                        display = f"🎵 {item}"
                    else:
                        display = f"📄 {item}"
                self.listbox.insert(tk.END, display)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать папку: {e}")

    def get_selected_full_path(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        display = self.listbox.get(sel[0])
        for prefix in ["📁 ", "📄 ", "🖼️ ", "🎵 "]:
            if display.startswith(prefix):
                name = display[len(prefix):]
                break
        else:
            if display and display[0] in "📁📄🖼️🎵":
                name = display[1:].lstrip()
            else:
                name = display
        name = name.strip()
        return os.path.join(self.current_path, name)

    def open_selected(self):
        full_path = self.get_selected_full_path()
        if not full_path:
            messagebox.showwarning("Ошибка", "Выберите элемент")
            return
        if os.path.isdir(full_path):
            self.current_path = full_path
            self.refresh()
        elif os.path.isfile(full_path):
            ext = os.path.splitext(full_path)[1].lower()
            if ext == ".txt":
                self.open_in_notepad(full_path)
            elif ext == ".png":
                Painter(self.parent, self.taskbar, filepath=full_path)
            elif ext == ".mp3":
                MusicPlayer(self.parent, self.taskbar, filepath=full_path)
            else:
                messagebox.showinfo("Информация", "Поддерживаются .txt, .png и .mp3")
        else:
            messagebox.showerror("Ошибка", "Элемент не является файлом или папкой")

    def go_back(self):
        if self.current_path == self.root_folder:
            return
        parent = os.path.dirname(self.current_path)
        if parent.startswith(self.root_folder) or parent == self.root_folder:
            self.current_path = parent
            self.refresh()

    def delete_selected(self):
        full_path = self.get_selected_full_path()
        if not full_path:
            messagebox.showwarning("Ошибка", "Выберите элемент")
            return
        name = os.path.basename(full_path)
        if messagebox.askyesno("Удалить", f"Удалить '{name}'?"):
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def rename_selected(self):
        full_path = self.get_selected_full_path()
        if not full_path:
            messagebox.showwarning("Ошибка", "Выберите элемент")
            return
        old_name = os.path.basename(full_path)
        new_name = simpledialog.askstring("Переименовать", f"Введите новое имя для '{old_name}':", parent=self.window)
        if new_name:
            new_path = os.path.join(self.current_path, new_name.strip().replace(" ", "_"))
            if not os.path.exists(new_path):
                try:
                    os.rename(full_path, new_path)
                    self.refresh()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось переименовать: {e}")
            else:
                messagebox.showerror("Ошибка", "Файл/папка с таким именем уже существует")

    def copy_selected(self):
        full_path = self.get_selected_full_path()
        if not full_path:
            messagebox.showwarning("Ошибка", "Выберите элемент")
            return
        self.clipboard = (full_path, 'copy')
        messagebox.showinfo("Копировать", f"Скопировано: {os.path.basename(full_path)}")

    def cut_selected(self):
        full_path = self.get_selected_full_path()
        if not full_path:
            messagebox.showwarning("Ошибка", "Выберите элемент")
            return
        self.clipboard = (full_path, 'cut')
        messagebox.showinfo("Вырезать", f"Вырезано: {os.path.basename(full_path)}")

    def paste_clipboard(self):
        if self.clipboard is None:
            messagebox.showwarning("Ошибка", "Буфер обмена пуст")
            return
        src_path, action = self.clipboard
        src_name = os.path.basename(src_path)
        dst_path = os.path.join(self.current_path, src_name)

        base, ext = os.path.splitext(src_name)
        counter = 1
        while os.path.exists(dst_path):
            new_name = f"{base} ({counter}){ext}"
            dst_path = os.path.join(self.current_path, new_name)
            counter += 1

        try:
            if action == 'copy':
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
                messagebox.showinfo("Вставить", f"Скопировано: {src_name}")
            elif action == 'cut':
                shutil.move(src_path, dst_path)
                messagebox.showinfo("Вставить", f"Перемещено: {src_name}")
                self.clipboard = None
            self.refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить: {e}")

    def show_context_menu(self, event):
        item = self.listbox.nearest(event.y)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(item)
        self.listbox.activate(item)
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Открыть", command=self.open_selected)
        menu.add_command(label="Копировать", command=self.copy_selected)
        menu.add_command(label="Вырезать", command=self.cut_selected)
        menu.add_separator()
        menu.add_command(label="Вставить", command=self.paste_clipboard)
        menu.add_separator()
        menu.add_command(label="Переименовать", command=self.rename_selected)
        menu.add_command(label="Удалить", command=self.delete_selected)
        menu.post(event.x_root, event.y_root)

    def new_folder(self):
        name = simpledialog.askstring("Новая папка", "Введите имя папки:", parent=self.window)
        if name:
            new_path = os.path.join(self.current_path, name.strip().replace(" ", "_"))
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                self.refresh()
            else:
                messagebox.showerror("Ошибка", "Папка уже существует")

    def new_text_file(self):
        name = simpledialog.askstring("Новый файл", "Имя файла (без расширения):", parent=self.window)
        if name:
            filename = name.strip().replace(" ", "_") + ".txt"
            full_path = os.path.join(self.current_path, filename)
            if not os.path.exists(full_path):
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("")
                self.refresh()
            else:
                messagebox.showerror("Ошибка", "Файл уже существует")

    def new_picture(self):
        Painter(self.parent, self.taskbar, filepath=None)
        self.refresh()

    def upload_music(self):
        filetypes = [("MP3 файлы", "*.mp3"), ("Все файлы", "*.*")]
        src = filedialog.askopenfilename(title="Выберите MP3 файл", filetypes=filetypes)
        if src:
            dst = os.path.join(self.current_path, os.path.basename(src))
            try:
                shutil.copy2(src, dst)
                self.refresh()
                messagebox.showinfo("Успех", f"Файл {os.path.basename(src)} скопирован")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось скопировать: {e}")

    def open_in_notepad(self, path):
        win = tk.Toplevel(self.parent)
        win.title("Блокнот - " + os.path.basename(path))
        win.geometry("500x400")
        win.transient(self.parent)
        win.lift()
        win.focus_force()
        self.taskbar.add_window(win, os.path.basename(path))

        text_area = tk.Text(win, wrap="word", font=("Consolas", 12))
        text_area.pack(fill="both", expand=True, padx=5, pady=5)

        try:
            with open(path, "r", encoding="utf-8") as f:
                text_area.insert("1.0", f.read())
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        def save():
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text_area.get("1.0", tk.END).rstrip("\n"))
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(win, text="Сохранить", command=save).pack(pady=5)

        def on_close():
            save()
            self.taskbar.remove_window(win)
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", on_close)