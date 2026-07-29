import tkinter as tk
import random


class Sapper:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar
        self.rows = 9
        self.cols = 9
        self.mines = 10
        self.buttons = []
        self.mine_positions = set()
        self.opened = set()
        self.flags = set()
        self.game_over = False

        self.window = tk.Toplevel(parent)
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()
        self.window.title("Сапёр")
        self.window.resizable(False, False)
        self.taskbar.add_window(self.window, "Сапёр")

        # Верхняя панель: счётчик флагов и кнопка новой игры
        top_frame = tk.Frame(self.window)
        top_frame.pack(pady=5)
        self.flag_label = tk.Label(top_frame, text=f"🚩 {self.mines - len(self.flags)}", font=("Arial", 14))
        self.flag_label.pack(side="left", padx=10)
        self.restart_btn = tk.Button(top_frame, text="Новая игра", command=self.restart)
        self.restart_btn.pack(side="left", padx=10)

        # Основное поле
        self.frame = tk.Frame(self.window)
        self.frame.pack()

        self.restart()

    def restart(self):
        # Очищаем старое поле
        for row in self.buttons:
            for btn in row:
                btn.destroy()
        self.buttons.clear()
        self.mine_positions.clear()
        self.opened.clear()
        self.flags.clear()
        self.game_over = False

        # Генерируем мины
        self.mine_positions = set()
        while len(self.mine_positions) < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            self.mine_positions.add((r, c))

        # Создаём кнопки
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                btn = tk.Button(self.frame, width=2, height=1, font=("Arial", 12),
                                command=lambda r=r, c=c: self.left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.right_click(r, c))
                btn.grid(row=r, column=c, padx=1, pady=1)
                row.append(btn)
            self.buttons.append(row)

        self.update_flag_display()

    def update_flag_display(self):
        remaining = self.mines - len(self.flags)
        self.flag_label.config(text=f"🚩 {remaining}")

    def left_click(self, r, c):
        if self.game_over:
            return
        if (r, c) in self.flags:
            return
        if (r, c) in self.mine_positions:
            self.lose()
            return
        self.reveal(r, c)
        self.check_win()

    def right_click(self, r, c):
        if self.game_over:
            return
        if (r, c) in self.opened:
            return
        if (r, c) in self.flags:
            self.flags.remove((r, c))
            self.buttons[r][c].config(text="", bg="SystemButtonFace")
        else:
            if len(self.flags) < self.mines:
                self.flags.add((r, c))
                self.buttons[r][c].config(text="🚩", bg="lightyellow")
        self.update_flag_display()
        self.check_win()

    def reveal(self, r, c):
        if (r, c) in self.opened or (r, c) in self.flags:
            return
        self.opened.add((r, c))
        count = self.count_adjacent_mines(r, c)
        btn = self.buttons[r][c]
        if count == 0:
            btn.config(text="", bg="lightgray", state="disabled", relief="sunken")
            # Открываем соседей
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if (nr, nc) not in self.opened and (nr, nc) not in self.flags:
                            self.reveal(nr, nc)
        else:
            color = {1: "blue", 2: "green", 3: "red", 4: "darkblue", 5: "brown", 6: "cyan", 7: "black", 8: "gray"}.get(
                count, "black")
            btn.config(text=str(count), fg=color, bg="lightgray", state="disabled", relief="sunken")

    def count_adjacent_mines(self, r, c):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) in self.mine_positions:
                        count += 1
        return count

    def lose(self):
        self.game_over = True
        # Показываем все мины
        for r, c in self.mine_positions:
            if (r, c) not in self.flags:
                self.buttons[r][c].config(text="💣", bg="red")
        # Блокируем все кнопки
        for r in range(self.rows):
            for c in range(self.cols):
                self.buttons[r][c].config(state="disabled")
        # Сообщение
        tk.messagebox.showinfo("Сапёр", "Вы подорвались! Игра окончена.")

    def check_win(self):
        # Победа, если открыты все клетки, кроме мин
        opened_without_mines = len(self.opened)
        total_cells_without_mines = self.rows * self.cols - self.mines
        if opened_without_mines == total_cells_without_mines:
            self.game_over = True
            tk.messagebox.showinfo("Сапёр", "Поздравляем! Вы выиграли!")
            # Можно добавить перезапуск