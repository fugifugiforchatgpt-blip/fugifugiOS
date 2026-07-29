import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from gigachat import GigaChat
from config import GIGACHAT_CREDENTIALS

class GigaChatAssistant:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar
        self.window = tk.Toplevel(parent)
        self.window.title("Ассистент (GigaChat)")
        self.window.geometry("700x550")
        self.window.minsize(500, 400)
        self.taskbar.add_window(self.window, "Ассистент")

        self.chat_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, state='disabled', font=("Segoe UI", 10))
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.Frame(self.window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.input_field = tk.Entry(input_frame, font=("Segoe UI", 10))
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", self.send_message)

        send_button = tk.Button(input_frame, text="Отправить", command=self.send_message, width=10)
        send_button.pack(side=tk.RIGHT)

        clear_button = tk.Button(self.window, text="Очистить историю", command=self.clear_chat, width=15)
        clear_button.pack(pady=5)

        self.giga_client = GigaChat(
            credentials=GIGACHAT_CREDENTIALS,
            verify_ssl_certs=False
        )

        self.display_message("Ассистент", "Привет! Я твой ИИ-помощник. Задавай любые вопросы!", "assistant")

    def send_message(self, event=None):
        user_message = self.input_field.get().strip()
        if not user_message:
            return
        self.input_field.delete(0, tk.END)

        self.display_message("Вы", user_message, "user")
        threading.Thread(target=self.get_gigachat_response, args=(user_message,), daemon=True).start()

    def get_gigachat_response(self, prompt):
        try:
            response = self.giga_client.chat(prompt)
            assistant_reply = response.choices[0].message.content
            self.window.after(0, self.display_message, "Ассистент", assistant_reply, "assistant")
        except Exception as e:
            self.window.after(0, messagebox.showerror, "Ошибка", f"Ошибка GigaChat: {e}")

    def display_message(self, sender, message, msg_type):
        self.chat_area['state'] = 'normal'
        tag = f"msg_{msg_type}"
        self.chat_area.insert(tk.END, f"{sender}: ", tag)
        self.chat_area.insert(tk.END, f"{message}\n\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area['state'] = 'disabled'
        self.chat_area.tag_config("msg_user", foreground="blue")
        self.chat_area.tag_config("msg_assistant", foreground="green")

    def clear_chat(self):
        self.chat_area['state'] = 'normal'
        self.chat_area.delete(1.0, tk.END)
        self.chat_area['state'] = 'disabled'
        self.display_message("Ассистент", "История очищена. Задавай новые вопросы!", "assistant")