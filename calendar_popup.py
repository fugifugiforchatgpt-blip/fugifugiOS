import tkinter as tk
import calendar
from datetime import datetime
from theme_utils import get_theme  # импортируем функцию получения темы

class CalendarPopup:
    def __init__(self, master, x, y):
        self.window = tk.Toplevel(master)
        self.window.title("Календарь")
        self.window.resizable(False, False)

        # Определяем тему
        self.dark_mode = (get_theme() == "dark")
        if self.dark_mode:
            bg_color = "#2b2b2b"
            fg_color = "white"
            btn_bg = "#4a4a4a"
            btn_fg = "white"
            top_bg = "#1e1e1e"
        else:
            bg_color = "white"
            fg_color = "black"
            btn_bg = "lightgray"
            btn_fg = "black"
            top_bg = "lightgray"

        self.window.configure(bg=bg_color)

        # Размер и позиция
        width, height = 350, 300
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = screen_height - height - 10
        self.window.geometry(f"{width}x{height}+{x}+{y}")

        # Текущая дата
        self.today = datetime.now()
        self.current_year = self.today.year
        self.current_month = self.today.month

        # Верхняя панель
        top = tk.Frame(self.window, bg=top_bg)
        top.pack(fill=tk.X)
        tk.Button(top, text="◀", command=self.prev_month, font=("Arial", 12),
                  bg=btn_bg, fg=btn_fg, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        self.month_label = tk.Label(top, text="", font=("Arial", 12, "bold"),
                                    bg=top_bg, fg=fg_color)
        self.month_label.pack(side=tk.LEFT, expand=True)
        tk.Button(top, text="▶", command=self.next_month, font=("Arial", 12),
                  bg=btn_bg, fg=btn_fg, relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)

        # Календарная сетка
        self.cal_frame = tk.Frame(self.window, bg=bg_color)
        self.cal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.show_month()

    def show_month(self):
        for w in self.cal_frame.winfo_children():
            w.destroy()
        # Заголовки дней недели
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, d in enumerate(days):
            lbl = tk.Label(self.cal_frame, text=d, font=("Arial", 10, "bold"),
                           bg=self.cal_frame.cget("bg"), fg="gray")
            lbl.grid(row=0, column=i, padx=8, pady=5)
        # Календарь
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                if day == 0:
                    text = ""
                else:
                    text = str(day)
                # Проверяем, является ли этот день сегодняшним
                is_today = (self.current_year == self.today.year and
                            self.current_month == self.today.month and
                            day == self.today.day)
                label_bg = self.cal_frame.cget("bg")
                label_fg = "white" if self.dark_mode else "black"
                if is_today:
                    # Подсветка: рамка или цвет фона
                    lbl = tk.Label(self.cal_frame, text=text, font=("Arial", 10, "bold"),
                                   bg="#3366cc" if not self.dark_mode else "#88aaff",
                                   fg="white", width=3, relief=tk.SUNKEN)
                else:
                    lbl = tk.Label(self.cal_frame, text=text, font=("Arial", 10),
                                   bg=label_bg, fg=label_fg, width=3)
                lbl.grid(row=row+1, column=col, padx=8, pady=2)
        # Название месяца и год
        month_names_ru = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        month_name = month_names_ru[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.show_month()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.show_month()