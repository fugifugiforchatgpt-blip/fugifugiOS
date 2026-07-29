import tkinter as tk


class Calculator:
    def __init__(self, parent, taskbar):
        self.window = tk.Toplevel(parent)
        self.window.transient(parent)
        self.window.lift()
        self.window.focus_force()
        self.window.title("Калькулятор")
        self.window.geometry("300x400")
        self.window.resizable(False, False)
        taskbar.add_window(self.window, "Калькулятор")

        self.display = tk.Entry(self.window, font=("Arial", 20), justify="right", bd=10)
        self.display.pack(fill="both", padx=10, pady=10)
        self.display.insert(0, "0")

        self.current = ""
        self.first = None
        self.operation = None

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        frame = tk.Frame(self.window)
        frame.pack(expand=True, fill="both")
        row, col = 0, 0
        for btn_text in buttons:
            bg_color = "orange" if btn_text in "+-*/=" else "lightgray"
            cmd = lambda x=btn_text: self.on_button_click(x)
            btn = tk.Button(frame, text=btn_text, font=("Arial", 14), bg=bg_color,
                            command=cmd, width=5, height=2)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            col += 1
            if col > 3:
                col = 0
                row += 1
        btn_clear = tk.Button(frame, text="C", font=("Arial", 14), bg="red", fg="white",
                              command=self.clear, width=5, height=2)
        btn_clear.grid(row=row, column=0, columnspan=4, sticky="nsew", padx=2, pady=2)
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            frame.grid_rowconfigure(i, weight=1)

    def on_button_click(self, char):
        if char.isdigit() or char == '.':
            if char == '.' and '.' in self.current:
                return
            self.current += char
            self.display.delete(0, tk.END)
            self.display.insert(0, self.current)
        elif char in "+-*/":
            if self.current:
                self.first = float(self.current)
                self.operation = char
                self.current = ""
        elif char == '=':
            if self.first is not None and self.operation and self.current:
                second = float(self.current)
                try:
                    if self.operation == '+':
                        result = self.first + second
                    elif self.operation == '-':
                        result = self.first - second
                    elif self.operation == '*':
                        result = self.first * second
                    elif self.operation == '/':
                        if second == 0:
                            result = "Ошибка: деление на 0"
                        else:
                            result = self.first / second
                except Exception:
                    result = "Ошибка"
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
                self.first = None
                self.operation = None
                self.current = ""
                if isinstance(result, float) and result != "Ошибка: деление на 0":
                    self.current = str(result)

    def clear(self):
        self.current = ""
        self.first = None
        self.operation = None
        self.display.delete(0, tk.END)
        self.display.insert(0, "0")