import tkinter as tk
import random


class Tetris:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar

        # Параметры поля
        self.width = 10
        self.height = 20
        self.cell_size = 30
        self.board = [[0] * self.width for _ in range(self.height)]

        # Фигуры (тетрамино)
        self.shapes = [
            [[1, 1, 1, 1]],  # I
            [[1, 1], [1, 1]],  # O
            [[0, 1, 0], [1, 1, 1]],  # T
            [[1, 0, 0], [1, 1, 1]],  # L
            [[0, 0, 1], [1, 1, 1]],  # J
            [[0, 1, 1], [1, 1, 0]],  # S
            [[1, 1, 0], [0, 1, 1]]  # Z
        ]
        self.colors = ['cyan', 'yellow', 'purple', 'orange', 'blue', 'green', 'red']

        self.current_shape = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.game_over = False
        self.fall_interval = 500  # мс
        self.after_id = None

        # Создание окна игры
        self.window = tk.Toplevel(parent)
        self.window.title("Тетрис")
        self.window.geometry(f"{self.width * self.cell_size + 200}x{self.height * self.cell_size + 50}")
        self.window.resizable(False, False)
        self.taskbar.add_window(self.window, "Тетрис")
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()

        # Холст для игрового поля
        self.canvas = tk.Canvas(self.window, width=self.width * self.cell_size,
                                height=self.height * self.cell_size, bg='black')
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Панель информации справа
        info_frame = tk.Frame(self.window, bg='lightgray')
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.score_label = tk.Label(info_frame, text="Счёт: 0", font=("Arial", 16), bg='lightgray')
        self.score_label.pack(pady=10)

        self.next_label = tk.Label(info_frame, text="Следующая:", font=("Arial", 14), bg='lightgray')
        self.next_label.pack(pady=5)

        # Холст для превью следующей фигуры
        self.preview_canvas = tk.Canvas(info_frame, width=120, height=120, bg='black')
        self.preview_canvas.pack(pady=10)

        # Кнопки управления
        tk.Button(info_frame, text="🔄 Новая игра", command=self.restart, width=12).pack(pady=5)
        tk.Button(info_frame, text="❌ Закрыть", command=self.on_close, width=12).pack(pady=5)

        # Привязка клавиш
        self.window.bind("<Left>", self.move_left)
        self.window.bind("<Right>", self.move_right)
        self.window.bind("<Down>", self.move_down)
        self.window.bind("<Up>", self.rotate)
        self.window.bind("<space>", self.hard_drop)

        # Запуск игры
        self.restart()

    def new_piece(self):
        """Создаёт новую фигуру"""
        if not hasattr(self, 'next_shape'):
            self.next_shape = random.randint(0, len(self.shapes) - 1)
            self.next_color = self.colors[self.next_shape]
        shape_idx = self.next_shape
        color = self.next_color

        # Генерируем следующую фигуру
        self.next_shape = random.randint(0, len(self.shapes) - 1)
        self.next_color = self.colors[self.next_shape]
        self.update_preview()

        self.current_shape = [row[:] for row in self.shapes[shape_idx]]
        self.current_color = color
        self.current_x = self.width // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0

        if self.collision():
            self.game_over = True
            if self.after_id:
                self.window.after_cancel(self.after_id)
            self.canvas.create_text(self.width * self.cell_size // 2,
                                    self.height * self.cell_size // 2,
                                    text="GAME OVER", fill="red", font=("Arial", 24))
            return False
        return True

    def collision(self):
        """Проверяет столкновение текущей фигуры с границами или другими блоками"""
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = self.current_x + x
                    board_y = self.current_y + y
                    if (board_x < 0 or board_x >= self.width or
                            board_y >= self.height or
                            (board_y >= 0 and self.board[board_y][board_x])):
                        return True
        return False

    def merge(self):
        """Закрепляет текущую фигуру на поле"""
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.current_y + y][self.current_x + x] = self.current_color
        self.clear_lines()
        if not self.new_piece():
            return
        self.draw_board()

    def clear_lines(self):
        """Удаляет заполненные строки и увеличивает счёт"""
        lines_cleared = 0
        y = self.height - 1
        while y >= 0:
            if all(self.board[y]):
                del self.board[y]
                self.board.insert(0, [0] * self.width)
                lines_cleared += 1
            else:
                y -= 1
        if lines_cleared:
            self.score += [0, 100, 200, 400, 800][lines_cleared]  # очки за 1,2,3,4 линии
            self.score_label.config(text=f"Счёт: {self.score}")
            # Ускорение со временем (необязательно)
            # self.fall_interval = max(100, 500 - (self.score // 500) * 20)

    def draw_board(self):
        """Рисует всё поле и текущую фигуру"""
        self.canvas.delete("all")
        # Рисуем закреплённые блоки
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x]:
                    color = self.board[y][x]
                    self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size,
                                                 (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                                 fill=color, outline='gray')
        # Рисуем текущую фигуру
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.canvas.create_rectangle((self.current_x + x) * self.cell_size,
                                                 (self.current_y + y) * self.cell_size,
                                                 (self.current_x + x + 1) * self.cell_size,
                                                 (self.current_y + y + 1) * self.cell_size,
                                                 fill=self.current_color, outline='gray')

    def update_preview(self):
        """Рисует следующую фигуру на превью"""
        self.preview_canvas.delete("all")
        shape = self.shapes[self.next_shape]
        color = self.next_color
        cell_size = 20
        offset_x = (120 - len(shape[0]) * cell_size) // 2
        offset_y = (120 - len(shape) * cell_size) // 2
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.preview_canvas.create_rectangle(offset_x + x * cell_size,
                                                         offset_y + y * cell_size,
                                                         offset_x + (x + 1) * cell_size,
                                                         offset_y + (y + 1) * cell_size,
                                                         fill=color, outline='gray')

    def move_left(self, event=None):
        if not self.game_over:
            self.current_x -= 1
            if self.collision():
                self.current_x += 1
            else:
                self.draw_board()

    def move_right(self, event=None):
        if not self.game_over:
            self.current_x += 1
            if self.collision():
                self.current_x -= 1
            else:
                self.draw_board()

    def move_down(self, event=None):
        if not self.game_over:
            self.current_y += 1
            if self.collision():
                self.current_y -= 1
                self.merge()
            self.draw_board()

    def rotate(self, event=None):
        if not self.game_over:
            # Поворот фигуры на 90 градусов
            rotated = list(zip(*self.current_shape[::-1]))
            original_shape = self.current_shape
            self.current_shape = [list(row) for row in rotated]
            if self.collision():
                self.current_shape = original_shape
            else:
                self.draw_board()

    def hard_drop(self, event=None):
        if not self.game_over:
            while not self.collision():
                self.current_y += 1
            self.current_y -= 1
            self.merge()
            self.draw_board()

    def fall(self):
        if not self.game_over:
            self.current_y += 1
            if self.collision():
                self.current_y -= 1
                self.merge()
            self.draw_board()
            self.after_id = self.window.after(self.fall_interval, self.fall)

    def restart(self):
        # Сброс игры
        self.board = [[0] * self.width for _ in range(self.height)]
        self.score = 0
        self.game_over = False
        self.score_label.config(text="Счёт: 0")
        if self.after_id:
            self.window.after_cancel(self.after_id)
        self.next_shape = random.randint(0, len(self.shapes) - 1)
        self.next_color = self.colors[self.next_shape]
        self.new_piece()
        self.draw_board()
        self.fall()

    def on_close(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
        self.taskbar.remove_window(self.window)
        self.window.destroy()