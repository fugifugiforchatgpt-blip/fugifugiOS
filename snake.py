import tkinter as tk
import random

# ------------------------------------------------------------
# Класс главного меню (выбор режима, сложности)
# ------------------------------------------------------------
class SnakeGame:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar
        self.current_game = None
        self.show_main_menu()

    def show_main_menu(self):
        if self.current_game:
            self.current_game.destroy_game()
            self.current_game = None

        self.menu_window = tk.Toplevel(self.parent)
        self.menu_window.title("Змейка – Главное меню")
        self.menu_window.geometry("500x400")
        self.menu_window.resizable(False, False)
        self.menu_window.transient(self.parent)
        self.menu_window.grab_set()
        self.menu_window.configure(bg="#1a1a2e")
        self.taskbar.add_window(self.menu_window, "Змейка (меню)")
        self.menu_window.protocol("WM_DELETE_WINDOW", self.exit_game)

        tk.Label(self.menu_window, text="🐍 ЗМЕЙКА 🐍", font=("Arial", 28, "bold"),
                 bg="#1a1a2e", fg="#e94560").pack(pady=30)

        tk.Button(self.menu_window, text="🎮 Играть одному", font=("Arial", 16),
                  bg="#0f3460", fg="white", activebackground="#16213e",
                  width=20, height=2, command=self.start_single).pack(pady=15)

        tk.Button(self.menu_window, text="🤖 Играть с ИИ", font=("Arial", 16),
                  bg="#0f3460", fg="white", activebackground="#16213e",
                  width=20, height=2, command=self.show_difficulty_menu).pack(pady=15)

        tk.Button(self.menu_window, text="❌ Выйти из игры", font=("Arial", 12),
                  bg="#533483", fg="white", activebackground="#3a1f6e",
                  width=20, command=self.exit_game).pack(pady=30)

    def show_difficulty_menu(self):
        self.menu_window.destroy()
        self.diff_window = tk.Toplevel(self.parent)
        self.diff_window.title("Змейка – Выбор сложности")
        self.diff_window.geometry("500x400")
        self.diff_window.resizable(False, False)
        self.diff_window.transient(self.parent)
        self.diff_window.grab_set()
        self.diff_window.configure(bg="#1a1a2e")
        self.taskbar.add_window(self.diff_window, "Змейка (сложность)")
        self.diff_window.protocol("WM_DELETE_WINDOW", self.back_to_main_menu)

        tk.Label(self.diff_window, text="Выбери сложность ИИ", font=("Arial", 24, "bold"),
                 bg="#1a1a2e", fg="#e94560").pack(pady=30)
        tk.Label(self.diff_window, text="(Твоя змейка всегда одинаковой скорости)",
                 font=("Arial", 12), bg="#1a1a2e", fg="#aaa").pack(pady=5)

        tk.Button(self.diff_window, text="🍃 Лёгкая (ИИ очень медленный)", font=("Arial", 14),
                  bg="#2c5e2e", fg="white", width=25, height=2,
                  command=lambda: self.start_ai_game("easy")).pack(pady=10)

        tk.Button(self.diff_window, text="⚡ Средняя (ИИ обычный)", font=("Arial", 14),
                  bg="#d4af37", fg="black", width=25, height=2,
                  command=lambda: self.start_ai_game("medium")).pack(pady=10)

        tk.Button(self.diff_window, text="🔥 Сложная (ИИ быстрый)", font=("Arial", 14),
                  bg="#a13333", fg="white", width=25, height=2,
                  command=lambda: self.start_ai_game("hard")).pack(pady=10)

        tk.Button(self.diff_window, text="◀ Назад", font=("Arial", 12),
                  bg="#533483", fg="white", width=15, command=self.back_to_main_menu).pack(pady=30)

    def back_to_main_menu(self):
        if hasattr(self, 'diff_window') and self.diff_window:
            try:
                self.taskbar.remove_window(self.diff_window)
            except:
                pass
            self.diff_window.destroy()
        self.show_main_menu()

    def start_single(self):
        if hasattr(self, 'menu_window'):
            self.menu_window.destroy()
        self.start_game("single")

    def start_ai_game(self, difficulty):
        if hasattr(self, 'diff_window'):
            self.diff_window.destroy()
        self.start_game("ai", difficulty)

    def start_game(self, mode, difficulty=None):
        if self.current_game:
            self.current_game.destroy_game()
        self.current_game = GameWindow(self.parent, self.taskbar, mode, difficulty, self.on_game_closed)

    def on_game_closed(self):
        self.current_game = None
        self.show_main_menu()

    def exit_game(self):
        if self.current_game:
            self.current_game.destroy_game()
            self.current_game = None
        if hasattr(self, 'menu_window') and self.menu_window:
            try:
                self.taskbar.remove_window(self.menu_window)
            except:
                pass
            self.menu_window.destroy()


# ------------------------------------------------------------
# Класс окна игры (без джойстика, только клавиатура)
# ------------------------------------------------------------
class GameWindow:
    def __init__(self, parent, taskbar, mode, difficulty, on_close_callback):
        self.parent = parent
        self.taskbar = taskbar
        self.mode = mode
        self.difficulty = difficulty
        self.on_close_callback = on_close_callback
        self.after_id = None
        self.closing = False

        # Параметры поля
        self.field_size = 20
        self.cell_size = 25
        self.width = self.field_size * self.cell_size
        self.height = self.field_size * self.cell_size

        if self.mode == "ai":
            if self.difficulty == "easy":
                self.ai_step_every = 4
            elif self.difficulty == "medium":
                self.ai_step_every = 2
            else:
                self.ai_step_every = 1
            self.ai_step_counter = 0
        else:
            self.ai_step_every = None

        # Создаём окно игры
        title = "Змейка – Одиночная игра" if self.mode == "single" else f"Змейка – Против ИИ (сложность: {self.difficulty})"
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(f"{self.width+20}x{self.height+120}")
        self.window.resizable(False, False)
        self.taskbar.add_window(self.window, "Змейка")
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.window.focus_set()

        # Холст
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg='black')
        self.canvas.pack(pady=10)

        # Панель счёта и кнопок
        info_frame = tk.Frame(self.window)
        info_frame.pack()

        if self.mode == "single":
            self.score_label = tk.Label(info_frame, text="Счёт: 0", font=("Arial", 14))
        else:
            self.score_label = tk.Label(info_frame, text="Игрок: 0   ИИ: 0", font=("Arial", 14))
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.restart_btn = tk.Button(info_frame, text="Новая игра", command=self.restart)
        self.restart_btn.pack(side=tk.LEFT, padx=5)

        self.menu_btn = tk.Button(info_frame, text="Главное меню", command=self.exit_to_menu)
        self.menu_btn.pack(side=tk.LEFT, padx=5)

        self.restart()
        self.window.bind("<KeyPress>", self.change_direction)
        self.start_update()

    def exit_to_menu(self):
        if self.closing:
            return
        self.closing = True
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None
        try:
            self.taskbar.remove_window(self.window)
        except:
            pass
        try:
            self.window.destroy()
        except:
            pass
        self.on_close_callback()

    def destroy_game(self):
        if self.closing:
            return
        self.closing = True
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None
        try:
            self.window.destroy()
        except:
            pass

    # --- Игровая логика ---
    def restart(self):
        if self.closing:
            return
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        if self.mode == "single":
            self.player_snake = [(10, 10), (9, 10), (8, 10)]
            self.player_dir = "Right"
            self.player_next_dir = "Right"
            self.player_score = 0
            self.player_alive = True
            self.food = self.spawn_food_single()
            self.game_over = False
        else:
            self.player_snake = [(10, 10), (9, 10), (8, 10)]
            self.player_dir = "Right"
            self.player_next_dir = "Right"
            self.player_score = 0
            self.player_alive = True

            self.ai_snake = [(10, 15), (9, 15), (8, 15)]
            self.ai_dir = "Right"
            self.ai_next_dir = "Right"
            self.ai_score = 0
            self.ai_alive = True

            self.food = self.spawn_food_dual()
            self.game_over = False
            self.ai_step_counter = 0

        self.draw()
        self.window.focus_force()
        self.window.grab_set()
        self.window.focus_set()
        self.start_update()

    def start_update(self):
        if self.closing:
            return
        if self.after_id:
            self.window.after_cancel(self.after_id)
        self.update_game()

    def spawn_food_single(self):
        if self.closing:
            return None
        occupied = set(self.player_snake)
        free_cells = [(x, y) for x in range(self.field_size) for y in range(self.field_size) if (x, y) not in occupied]
        if not free_cells:
            return None
        return random.choice(free_cells)

    def spawn_food_dual(self):
        if self.closing:
            return None
        occupied = set(self.player_snake + self.ai_snake)
        free_cells = [(x, y) for x in range(self.field_size) for y in range(self.field_size) if (x, y) not in occupied]
        if not free_cells:
            return None
        return random.choice(free_cells)

    def change_direction(self, event):
        if self.closing or self.game_over:
            return
        key = event.keysym
        if self.mode == "single":
            if key == "Up" and self.player_dir != "Down":
                self.player_next_dir = "Up"
            elif key == "Down" and self.player_dir != "Up":
                self.player_next_dir = "Down"
            elif key == "Left" and self.player_dir != "Right":
                self.player_next_dir = "Left"
            elif key == "Right" and self.player_dir != "Left":
                self.player_next_dir = "Right"
        else:
            if key == "Up" and self.player_dir != "Down":
                self.player_next_dir = "Up"
            elif key == "Down" and self.player_dir != "Up":
                self.player_next_dir = "Down"
            elif key == "Left" and self.player_dir != "Right":
                self.player_next_dir = "Left"
            elif key == "Right" and self.player_dir != "Left":
                self.player_next_dir = "Right"

    def ai_decide_direction(self):
        head = self.ai_snake[0]
        fx, fy = self.food
        dx = fx - head[0]
        dy = fy - head[1]
        candidates = []
        if dx > 0:
            candidates.append("Right")
        elif dx < 0:
            candidates.append("Left")
        if dy > 0:
            candidates.append("Down")
        elif dy < 0:
            candidates.append("Up")
        all_dirs = ["Up", "Down", "Left", "Right"]
        for d in all_dirs:
            if d not in candidates:
                candidates.append(d)
        for d in candidates:
            new_head = self.get_new_head(self.ai_snake[0], d)
            if self.is_safe_for_ai(new_head):
                return d
        return self.ai_dir

    def get_new_head(self, head, direction):
        x, y = head
        if direction == "Up":
            return (x, y-1)
        elif direction == "Down":
            return (x, y+1)
        elif direction == "Left":
            return (x-1, y)
        else:
            return (x+1, y)

    def is_safe_for_ai(self, pos):
        x, y = pos
        if x < 0 or x >= self.field_size or y < 0 or y >= self.field_size:
            return False
        if pos in self.ai_snake:
            return False
        if pos in self.player_snake:
            return False
        return True

    def update_game(self):
        if self.closing:
            return
        if self.game_over:
            self.after_id = self.window.after(100, self.update_game)
            return

        if self.mode == "single":
            self.player_dir = self.player_next_dir
            if self.player_alive:
                new_head = self.get_new_head(self.player_snake[0], self.player_dir)
                if new_head == self.food:
                    self.player_snake.insert(0, new_head)
                    self.player_score += 10
                    self.food = self.spawn_food_single()
                    if self.food is None:
                        self.game_over = True
                        self.show_winner("Победа! Поле заполнено")
                        self.after_id = self.window.after(100, self.update_game)
                        return
                else:
                    self.player_snake.insert(0, new_head)
                    self.player_snake.pop()
                if (new_head[0] < 0 or new_head[0] >= self.field_size or
                    new_head[1] < 0 or new_head[1] >= self.field_size or
                    new_head in self.player_snake[1:]):
                    self.player_alive = False
                    self.game_over = True
                    self.show_winner("Игра окончена! Ты врезался.")
                    self.after_id = self.window.after(100, self.update_game)
                    return
            self.score_label.config(text=f"Счёт: {self.player_score}")
            self.draw()
            self.after_id = self.window.after(100, self.update_game)
            return

        # Режим с ИИ
        self.player_dir = self.player_next_dir

        if self.player_alive:
            new_head_player = self.get_new_head(self.player_snake[0], self.player_dir)
            if new_head_player == self.food:
                self.player_snake.insert(0, new_head_player)
                self.player_score += 10
                self.food = self.spawn_food_dual()
                if self.food is None:
                    self.game_over = True
                    self.show_winner("Ничья! Поле заполнено")
                    self.after_id = self.window.after(100, self.update_game)
                    return
            else:
                self.player_snake.insert(0, new_head_player)
                self.player_snake.pop()
            if (new_head_player[0] < 0 or new_head_player[0] >= self.field_size or
                new_head_player[1] < 0 or new_head_player[1] >= self.field_size or
                new_head_player in self.player_snake[1:] or
                (self.ai_alive and new_head_player in self.ai_snake)):
                self.player_alive = False

        if self.ai_alive:
            self.ai_step_counter += 1
            if self.ai_step_counter >= self.ai_step_every:
                self.ai_step_counter = 0
                self.ai_dir = self.ai_decide_direction()
                new_head_ai = self.get_new_head(self.ai_snake[0], self.ai_dir)
                if new_head_ai == self.food:
                    self.ai_snake.insert(0, new_head_ai)
                    self.ai_score += 10
                    self.food = self.spawn_food_dual()
                    if self.food is None:
                        self.game_over = True
                        self.show_winner("Ничья! Поле заполнено")
                        self.after_id = self.window.after(100, self.update_game)
                        return
                else:
                    self.ai_snake.insert(0, new_head_ai)
                    self.ai_snake.pop()
                if (new_head_ai[0] < 0 or new_head_ai[0] >= self.field_size or
                    new_head_ai[1] < 0 or new_head_ai[1] >= self.field_size or
                    new_head_ai in self.ai_snake[1:] or
                    (self.player_alive and new_head_ai in self.player_snake)):
                    self.ai_alive = False

        self.score_label.config(text=f"Игрок: {self.player_score}   ИИ: {self.ai_score}")

        if not self.player_alive and not self.ai_alive:
            self.game_over = True
            self.show_winner("Ничья! Обе змейки погибли")
        elif not self.player_alive:
            self.game_over = True
            self.show_winner("Победил ИИ!")
        elif not self.ai_alive:
            self.game_over = True
            self.show_winner("Победил Игрок!")

        self.draw()
        self.after_id = self.window.after(100, self.update_game)

    def draw(self):
        if self.closing:
            return
        self.canvas.delete("all")
        if self.food:
            fx, fy = self.food
            self.canvas.create_rectangle(fx*self.cell_size, fy*self.cell_size,
                                         (fx+1)*self.cell_size, (fy+1)*self.cell_size,
                                         fill="yellow")
        for i, (x, y) in enumerate(self.player_snake):
            color = "lime" if i == 0 else "green"
            self.canvas.create_rectangle(x*self.cell_size, y*self.cell_size,
                                         (x+1)*self.cell_size, (y+1)*self.cell_size,
                                         fill=color, outline="darkgreen")
        if self.mode == "ai" and hasattr(self, 'ai_snake'):
            for i, (x, y) in enumerate(self.ai_snake):
                color = "red" if i == 0 else "darkred"
                self.canvas.create_rectangle(x*self.cell_size, y*self.cell_size,
                                             (x+1)*self.cell_size, (y+1)*self.cell_size,
                                             fill=color, outline="maroon")

    def show_winner(self, message):
        self.canvas.create_text(self.width//2, self.height//2,
                                text=message, fill="white", font=("Arial", 20))
        self.canvas.create_text(self.width//2, self.height//2+40,
                                text="Нажмите 'Новая игра'", fill="gray", font=("Arial", 14))