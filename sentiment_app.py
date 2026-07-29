import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog, filedialog
from datetime import datetime
import numpy as np
import json
import os
import threading
import re
import time
import random
from collections import defaultdict
from sklearn.model_selection import train_test_split
import base64
import io
import os

TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# -------------------------------
# 1. ДАННЫЕ (импорт из vocabulary.py)
# -------------------------------
try:
    from vocabulary import initial_data
except ImportError:
    initial_data = {}
    print("Предупреждение: vocabulary.py не найден, используется пустой словарь.")

HISTORY_FILE = "train_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    to_save = {phrase: int(label) for phrase, label in history.items()}
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)

history = load_history()
if initial_data:
    for phrase, label in initial_data.items():
        if phrase not in history:
            history[phrase] = label
    save_history(history)

# Глобальные переменные для данных
all_phrases = []
vocab = []
X_full = None
Y_full = None

def update_data():
    global all_phrases, vocab, X_full, Y_full
    all_phrases = list(history.keys())
    word_set = set()
    for phrase in all_phrases:
        for word in phrase.split():
            word_set.add(word)
    vocab = sorted(word_set)
    def vectorize(phrase):
        vec = np.zeros(len(vocab))
        for w in phrase.split():
            if w in vocab:
                vec[vocab.index(w)] = 1
        return vec
    X_full = np.array([vectorize(p) for p in all_phrases])
    Y_full = np.array([history[p] for p in all_phrases]).reshape(-1, 1)
    return vectorize

vectorize_func = update_data()
def vectorize(phrase):
    return vectorize_func(phrase)

# -------------------------------
# 2. КЛАСС НЕЙРОСЕТИ
# -------------------------------
class ExplainableNN:
    def __init__(self, input_dim, hidden_dim, lr=0.5):
        self.lr = lr
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.5
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = np.random.randn(hidden_dim, 1) * 0.5
        self.b2 = np.zeros((1, 1))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    def sigmoid_deriv(self, x):
        return x * (1 - x)
    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2
    def backward(self, X, y, out, lr):
        m = X.shape[0]
        d_out = out - y
        d_z2 = d_out * self.sigmoid_deriv(out)
        dW2 = np.dot(self.a1.T, d_z2) / m
        db2 = np.sum(d_z2, axis=0, keepdims=True) / m
        d_hidden = np.dot(d_z2, self.W2.T) * self.sigmoid_deriv(self.a1)
        dW1 = np.dot(X.T, d_hidden) / m
        db1 = np.sum(d_hidden, axis=0, keepdims=True) / m
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
    def batch_train(self, X, y, epochs, lr=None, callback=None):
        if lr is None:
            lr = self.lr
        for e in range(epochs):
            out = self.forward(X)
            self.backward(X, y, out, lr)
            if e % 500 == 0 or e == epochs - 1:
                loss = np.mean((out - y) ** 2)
                log_msg = f"Эпоха {e}, ошибка: {loss:.6f}"
                print(log_msg)
                if callback:
                    callback(log_msg, e, loss)
    def online_step(self, x, target, lr=0.2):
        x = x.reshape(1, -1)
        target = np.array([[target]])
        out = self.forward(x)
        self.backward(x, target, out, lr)
    def predict_raw(self, X):
        return self.forward(X)
    def predict(self, X):
        return np.round(self.forward(X)).astype(int)

nn = None
training_logs = []
training_epochs = []
training_losses = []

# -------------------------------
# 3. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# -------------------------------
def apply_exclamation_boost(phrase, raw_pred):
    if phrase.endswith('!'):
        if raw_pred > 0.5:
            boosted = raw_pred + (1 - raw_pred) * 0.3
        else:
            boosted = raw_pred - raw_pred * 0.3
        return max(0, min(1, boosted))
    return raw_pred

def split_sentences(text):
    sentences = re.split(r'[.!?]+', text)
    return [s.strip().lower() for s in sentences if s.strip()]

def analyze_paragraph(paragraph):
    sentences = split_sentences(paragraph)
    if not sentences:
        return "Нет предложений для анализа.", []
    results = []
    pos_count = 0
    neg_count = 0
    for sent in sentences:
        vec = vectorize(sent)
        raw = nn.predict_raw(vec.reshape(1, -1))[0][0]
        boosted = apply_exclamation_boost(sent, raw)
        guess = 1 if boosted > 0.5 else 0
        sentiment = "позитив" if guess == 1 else "негатив"
        results.append((sent, sentiment, boosted))
        if guess == 1:
            pos_count += 1
        else:
            neg_count += 1
    total = len(sentences)
    summary = f"Всего предложений: {total}, позитивных: {pos_count}, негативных: {neg_count}."
    if pos_count > neg_count:
        summary += " Общее настроение: ПОЗИТИВНОЕ."
    elif neg_count > pos_count:
        summary += " Общее настроение: НЕГАТИВНОЕ."
    else:
        summary += " Общее настроение: НЕЙТРАЛЬНОЕ."
    return summary, results

def get_autocomplete_options(prefix, max_suggestions=5):
    if not prefix:
        return []
    prefix_lower = prefix.lower()
    matches = [phrase for phrase in history.keys() if phrase.startswith(prefix_lower)]
    matches.sort(key=len)
    return matches[:max_suggestions]

def build_markov_chain():
    chain = defaultdict(list)
    for phrase in history.keys():
        words = phrase.split()
        if len(words) < 2:
            continue
        for i in range(len(words)-1):
            chain[words[i]].append(words[i+1])
        chain["<START>"].append(words[0])
    return chain

def generate_phrase(chain, start_word=None, max_words=8):
    if start_word and start_word in chain:
        current = start_word
    else:
        possible_starts = chain.get("<START>", [])
        if not possible_starts:
            return "Недостаточно данных для генерации."
        current = random.choice(possible_starts)
    result = [current]
    for _ in range(max_words-1):
        next_words = chain.get(current, [])
        if not next_words:
            break
        current = random.choice(next_words)
        result.append(current)
    return " ".join(result)

# -------------------------------
# 4. ГЛАВНОЕ ПРИЛОЖЕНИЕ
# -------------------------------
class SentimentApp:
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar
        self.window = tk.Toplevel(parent)
        self.window.title("Фуги Фуги ИИ")
        self.window.geometry("1900x1000")
        self.window.minsize(800, 700)
        self.taskbar.add_window(self.window, "Фуги Фуги ИИ")

        self.random_mode = False
        self.nn_trained = None
        self.saved_epochs = ""
        self.saved_hidden = ""
        self.last_analyzed_phrase = ""
        self.sarcasm_model = None
        self.reasoning_var = tk.BooleanVar(value=False)

        self.feedback_frame = None
        self.last_user_text = ""
        self.last_vec = None
        self.last_guess = None
        self.last_raw = None
        self.feedback_timer_id = None
        self.feedback_remaining = 0
        self.timer_label = None

        top_frame = tk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        row1 = tk.Frame(top_frame)
        row1.pack(fill=tk.X, pady=2)
        row2 = tk.Frame(top_frame)
        row2.pack(fill=tk.X, pady=2)

        tk.Label(row1, text="Эпох:").pack(side=tk.LEFT)
        self.epochs_var = tk.StringVar(value="4000")
        self.epochs_combo = ttk.Combobox(row1, textvariable=self.epochs_var,
                                         values=["500", "1000", "2000", "4000", "6000", "8000", "10000", "15000"],
                                         width=8, state='readonly')
        self.epochs_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(row1, text="Нейронов:").pack(side=tk.LEFT, padx=(10, 0))
        self.hidden_var = tk.StringVar(value="8")
        self.hidden_combo = ttk.Combobox(row1, textvariable=self.hidden_var,
                                         values=["4", "8", "12", "16", "24", "32", "48"],
                                         width=5, state='readonly')
        self.hidden_combo.pack(side=tk.LEFT, padx=5)

        self.train_btn = tk.Button(row1, text="🔄 Переобучить", command=self.retrain_model)
        self.train_btn.pack(side=tk.LEFT, padx=2)
        self.log_btn = tk.Button(row1, text="📋 Логи", command=self.show_logs)
        self.log_btn.pack(side=tk.LEFT, padx=2)
        self.graph_btn = tk.Button(row1, text="📈 График", command=self.show_graph)
        self.graph_btn.pack(side=tk.LEFT, padx=2)
        self.save_graph_btn = tk.Button(row1, text="💾 Сохранить график", command=self.save_graph_to_file)
        self.save_graph_btn.pack(side=tk.LEFT, padx=2)
        self.theme_btn = tk.Button(row1, text="🌙 Тёмная тема", command=self.toggle_nn_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=2)

        self.notebook_btn = tk.Button(row2, text="📓 Блокнот", command=self.open_notebook)
        self.notebook_btn.pack(side=tk.LEFT, padx=2)
        self.compose_btn = tk.Button(row2, text="✍️ Сочинялка", command=self.open_composer)
        self.compose_btn.pack(side=tk.LEFT, padx=2)
        self.expert_btn = tk.Button(row2, text="🧠 Эксперт", command=self.open_expert)
        self.expert_btn.pack(side=tk.LEFT, padx=2)
        self.tournament_btn = tk.Button(row2, text="🏆 Турнир", command=self.open_tournament_window)
        self.tournament_btn.pack(side=tk.LEFT, padx=2)
        self.autotune_btn = tk.Button(row2, text="🔧 Автоподбор", command=self.auto_tune)
        self.autotune_btn.pack(side=tk.LEFT, padx=2)
        self.save_weights_btn = tk.Button(row2, text="💾 Сохранить веса", command=self.save_weights)
        self.save_weights_btn.pack(side=tk.LEFT, padx=2)
        self.load_weights_btn = tk.Button(row2, text="📂 Загрузить веса", command=self.load_weights)
        self.load_weights_btn.pack(side=tk.LEFT, padx=2)
        self.help_btn = tk.Button(row2, text="❓ Справка", command=self.show_help)
        self.help_btn.pack(side=tk.LEFT, padx=2)
        self.random_btn = tk.Button(row2, text="🎲 Случайный режим", command=self.toggle_random_mode)
        self.random_btn.pack(side=tk.LEFT, padx=2)
        self.reasoning_check = tk.Checkbutton(row2, text="🧠 Режим рассуждения", variable=self.reasoning_var)
        self.reasoning_check.pack(side=tk.LEFT, padx=5)
        self.save_config_btn = tk.Button(row2, text="💾 Сохранить конфиг", command=self.save_config)
        self.save_config_btn.pack(side=tk.LEFT, padx=2)
        self.load_config_btn = tk.Button(row2, text="📂 Загрузить конфиг", command=self.load_config)
        self.load_config_btn.pack(side=tk.LEFT, padx=2)
        self.vis_btn = tk.Button(row2, text="🔬 Структура сети", command=self.visualize_network)
        self.vis_btn.pack(side=tk.LEFT, padx=2)


        self.status_label = tk.Label(row2, text="", fg="green")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.chat_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, state='disabled', font=("Segoe UI", 10))
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.Frame(self.window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        self.input_entry = tk.Entry(input_frame, font=("Segoe UI", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", self.process_input)
        self.input_entry.bind("<KeyRelease>", self.on_key_release)

        send_btn = tk.Button(input_frame, text="Отправить", command=self.process_input)
        send_btn.pack(side=tk.RIGHT)

        self.autocomplete_listbox = tk.Listbox(self.window, height=4, bg="#f0f0f0")
        self.autocomplete_listbox.place_forget()
        self.autocomplete_listbox.bind("<ButtonRelease-1>", self.on_autocomplete_select)

        clear_btn = tk.Button(self.window, text="Очистить диалог", command=self.clear_chat)
        clear_btn.pack(pady=5)

        self.input_frame = input_frame

        self.display_message("Система", "Привет! Выбери параметры и нажми 'Переобучить'.", "info")
        self.retrain_model()

    def open_digit_painter(self):
        # Убедимся, что большая нейросеть загружена
        if not hasattr(self, 'big_nn'):
            from big_nn import BigNeuralNetwork
            self.big_nn = BigNeuralNetwork()  # при первом вызове обучится
        # Открываем окно рисования
        DigitPainter(self.window, self.big_nn)

    def display_message(self, sender, message, msg_type):
        self.chat_area['state'] = 'normal'
        tag = f"msg_{msg_type}"
        self.chat_area.insert(tk.END, f"{sender}: ", tag)
        self.chat_area.insert(tk.END, f"{message}\n\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area['state'] = 'disabled'
        self.chat_area.tag_config("msg_user", foreground="lightblue" if getattr(self, 'dark_mode', False) else "blue")
        self.chat_area.tag_config("msg_assistant", foreground="lightgreen" if getattr(self, 'dark_mode', False) else "green")
        self.chat_area.tag_config("msg_info", foreground="gray")

    def clear_chat(self):
        self.chat_area['state'] = 'normal'
        self.chat_area.delete(1.0, tk.END)
        self.chat_area['state'] = 'disabled'
        self.hide_feedback_panel()

    def retrain_model(self):
        def train_thread():
            try:
                self.train_btn.config(state=tk.DISABLED)
                for btn in [self.log_btn, self.graph_btn, self.save_graph_btn, self.notebook_btn,
                            self.compose_btn, self.expert_btn, self.tournament_btn, self.autotune_btn,
                            self.save_weights_btn, self.load_weights_btn, self.help_btn, self.random_btn,
                            self.save_config_btn, self.load_config_btn, self.vis_btn]:
                    btn.config(state=tk.DISABLED)
                self.status_label.config(text="Подготовка данных...", fg="orange")
                self.window.update()

                global all_phrases, vocab, X_full, Y_full, vectorize_func
                all_phrases = list(history.keys())
                word_set = set()
                for phrase in all_phrases:
                    for word in phrase.split():
                        word_set.add(word)
                vocab = sorted(word_set)

                def new_vectorize(phrase):
                    vec = np.zeros(len(vocab))
                    for w in phrase.split():
                        if w in vocab:
                            vec[vocab.index(w)] = 1
                    return vec

                vectorize_func = new_vectorize
                global vectorize
                vectorize = vectorize_func
                X_full = np.array([vectorize(p) for p in all_phrases])
                Y_full = np.array([history[p] for p in all_phrases]).reshape(-1, 1)

                epochs = int(self.epochs_var.get())
                hidden = int(self.hidden_var.get())
                global training_logs, training_epochs, training_losses, nn
                training_logs = []
                training_epochs = []
                training_losses = []

                def log_callback(msg, epoch, loss):
                    training_logs.append(msg)
                    training_epochs.append(epoch)
                    training_losses.append(loss)

                nn = ExplainableNN(len(vocab), hidden, lr=0.5)
                self.status_label.config(text=f"Обучение {epochs} эпох...", fg="orange")
                start = time.time()
                nn.batch_train(X_full, Y_full, epochs=epochs, lr=0.5, callback=log_callback)
                elapsed = time.time() - start
                self.status_label.config(text=f"Готово (эпох: {epochs}, нейронов: {hidden}, время: {elapsed:.2f} с)",
                                         fg="green")
                self.random_mode = False
                self.random_btn.config(text="🎲 Случайный режим", bg="SystemButtonFace")
                self.display_message("Система", f"Обучение завершено за {elapsed:.2f} с.", "info")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обучения: {e}")
            finally:
                self.train_btn.config(state=tk.NORMAL)
                for btn in [self.log_btn, self.graph_btn, self.save_graph_btn, self.notebook_btn,
                            self.compose_btn, self.expert_btn, self.tournament_btn, self.autotune_btn,
                            self.save_weights_btn, self.load_weights_btn, self.help_btn, self.random_btn,
                            self.save_config_btn, self.load_config_btn, self.vis_btn]:
                    btn.config(state=tk.NORMAL)

        threading.Thread(target=train_thread, daemon=True).start()

    def show_logs(self):
        if not training_logs:
            messagebox.showinfo("Логи", "Логи отсутствуют.")
            return
        log_window = tk.Toplevel(self.window)
        log_window.title("Логи обучения")
        log_window.geometry("600x400")
        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, font=("Courier", 10))
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for line in training_logs:
            log_text.insert(tk.END, line + "\n")
        log_text.config(state=tk.DISABLED)

    def show_graph(self):
        if not training_losses:
            messagebox.showinfo("График", "Нет данных.")
            return
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(8, 5))
            plt.plot(training_epochs, training_losses, 'b-', linewidth=2)
            plt.title("Ошибка при обучении")
            plt.xlabel("Эпоха")
            plt.ylabel("Среднеквадратичная ошибка")
            plt.grid(True)
            plt.show()
        except ImportError:
            messagebox.showerror("Ошибка", "Установите matplotlib")

    def save_graph_to_file(self):
        if not training_losses:
            messagebox.showinfo("График", "Нет данных.")
            return
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(8, 5))
            plt.plot(training_epochs, training_losses, 'b-', linewidth=2)
            plt.title("Ошибка при обучении")
            plt.xlabel("Эпоха")
            plt.ylabel("Среднеквадратичная ошибка")
            plt.grid(True)
            filename = f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=150)
            messagebox.showinfo("Сохранено", f"График сохранён как {filename}")
            plt.close()
        except ImportError:
            messagebox.showerror("Ошибка", "Matplotlib не установлен.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def toggle_nn_theme(self):
        if not hasattr(self, 'dark_mode'):
            self.dark_mode = False
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            bg = "#2b2b2b"
            fg = "white"
            entry_bg = "#3c3c3c"
            btn_bg = "#4a4a4a"
            btn_fg = "white"
            self.theme_btn.config(text="☀️ Светлая тема")
        else:
            bg = "#f0f0f0"
            fg = "black"
            entry_bg = "white"
            btn_bg = "#e0e0e0"
            btn_fg = "black"
            self.theme_btn.config(text="🌙 Тёмная тема")
        self.window.configure(bg=bg)
        self.chat_area.configure(bg=bg, fg=fg, insertbackground=fg)
        self.input_entry.configure(bg=entry_bg, fg=fg, insertbackground=fg)
        for child in self.window.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=bg)
                for grand in child.winfo_children():
                    if isinstance(grand, (tk.Button, tk.Label)):
                        grand.configure(bg=btn_bg, fg=btn_fg)
        self.chat_area.tag_config("msg_user", foreground="lightblue" if self.dark_mode else "blue")
        self.chat_area.tag_config("msg_assistant", foreground="lightgreen" if self.dark_mode else "green")
        self.chat_area.tag_config("msg_info", foreground="gray")

    def open_notebook(self):
        if nn is None:
            messagebox.showinfo("Блокнот", "Нейросеть не обучена.")
            return
        notebook_win = tk.Toplevel(self.window)
        notebook_win.title("Блокнот настроений")
        notebook_win.geometry("700x500")
        tk.Label(notebook_win, text="Введите текст (несколько предложений):").pack(pady=5)
        text_area = scrolledtext.ScrolledText(notebook_win, wrap=tk.WORD, height=10)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        result_area = scrolledtext.ScrolledText(notebook_win, wrap=tk.WORD, height=8, state='disabled')
        result_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def analyze():
            paragraph = text_area.get("1.0", tk.END).strip()
            if not paragraph:
                return
            summary, results = analyze_paragraph(paragraph)
            result_area['state'] = 'normal'
            result_area.delete(1.0, tk.END)
            result_area.insert(tk.END, summary + "\n\n")
            for sent, sentiment, score in results:
                result_area.insert(tk.END, f"• {sent} → {sentiment} (уверенность {score:.0%})\n")
            result_area['state'] = 'disabled'

        tk.Button(notebook_win, text="Анализировать", command=analyze).pack(pady=5)

    def open_composer(self):
        if nn is None:
            messagebox.showinfo("Сочинялка", "Нейросеть не обучена.")
            return
        if len(history) < 5:
            messagebox.showinfo("Сочинялка", "Мало фраз в базе.")
            return
        chain = build_markov_chain()
        compose_win = tk.Toplevel(self.window)
        compose_win.title("Сочинялка")
        compose_win.geometry("500x300")
        tk.Label(compose_win, text="Введите начальное слово (или оставьте пустым):").pack(pady=5)
        word_entry = tk.Entry(compose_win, width=30)
        word_entry.pack(pady=5)
        result_text = tk.Text(compose_win, height=10, wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def generate():
            start = word_entry.get().strip().lower()
            phrase = generate_phrase(chain, start if start else None, max_words=10)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, phrase)

        tk.Button(compose_win, text="Сгенерировать", command=generate).pack(pady=5)

    def open_expert(self):
        if nn is None:
            messagebox.showinfo("Эксперт", "Нейросеть не обучена.")
            return
        phrase = self.last_analyzed_phrase
        if not phrase:
            phrase = simpledialog.askstring("Эксперт", "Введите фразу для анализа:", parent=self.window)
            if not phrase:
                return
            phrase = phrase.strip().lower()
        vec = vectorize(phrase)
        raw = nn.predict_raw(vec.reshape(1, -1))[0][0]
        boosted = apply_exclamation_boost(phrase, raw)
        guess = 1 if boosted > 0.5 else 0
        sentiment = "позитив" if guess == 1 else "негатив"
        confidence = boosted if boosted > 0.5 else 1 - boosted
        words = phrase.split()
        if not words:
            messagebox.showinfo("Эксперт", "Фраза не содержит слов.")
            return
        contributions = []
        for w in words:
            if w in vocab:
                idx = vocab.index(w)
                contrib = np.sum(nn.W1[idx, :] * nn.W2[:, 0])
                contributions.append(contrib)
            else:
                contributions.append(0.0)
        max_abs = max(abs(c) for c in contributions) if contributions else 1
        if max_abs == 0:
            max_abs = 1

        def get_color(contrib):
            intensity = abs(contrib) / max_abs
            intensity = min(1.0, intensity)
            if contrib > 0:
                r = 0
                g = int(200 + 55 * intensity)
                b = 0
            else:
                r = int(200 + 55 * intensity)
                g = 0
                b = 0
            return f"#{r:02x}{g:02x}{b:02x}"

        win = tk.Toplevel(self.window)
        win.title("Эксперт – влияние слов во фразе")
        win.geometry("800x600")
        win.configure(bg="white")
        tk.Label(win, text=f"Фраза: «{phrase}»", font=("Arial", 12, "bold"), bg="white").pack(pady=10)
        tk.Label(win, text=f"Тональность: {sentiment} (уверенность {confidence:.0%})",
                 fg="green" if guess == 1 else "red", bg="white").pack()
        canvas = tk.Canvas(win, bg="white", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        inner = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=inner, anchor="nw")
        for i, (w, contrib) in enumerate(zip(words, contributions)):
            frame = tk.Frame(inner, bg="white")
            frame.pack(anchor="w", pady=5)
            tk.Label(frame, text=w, font=("Arial", 11), bg="white", width=20, anchor="w").pack(side=tk.LEFT, padx=5)
            color = get_color(contrib)
            bar_len = 300 * (abs(contrib) / max_abs)
            canvas2 = tk.Canvas(frame, width=300, height=20, bg="white", highlightthickness=0)
            canvas2.pack(side=tk.LEFT, padx=5)
            canvas2.create_rectangle(0, 0, bar_len, 20, fill=color, outline="black")
            tk.Label(frame, text=f"{contrib:.4f}", font=("Arial", 9), bg="white", width=10).pack(side=tk.LEFT)
            if w not in vocab:
                tk.Label(frame, text="(не в словаре)", fg="gray", bg="white").pack(side=tk.LEFT)
        inner.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        leg_frame = tk.Frame(win, bg="white")
        leg_frame.pack(pady=10)
        tk.Label(leg_frame, text="🟢 Зелёный → позитив", fg="green", bg="white").pack(side=tk.LEFT, padx=10)
        tk.Label(leg_frame, text="🔴 Красный → негатив", fg="red", bg="white").pack(side=tk.LEFT, padx=10)
        tk.Label(leg_frame, text="Чем ярче, тем сильнее", bg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)

    def open_tournament_window(self):
        if nn is None:
            messagebox.showinfo("Турнир", "Сначала обучите основную модель.")
            return
        win = tk.Toplevel(self.window)
        win.title("Турнир нейросетей")
        win.geometry("700x600")
        frame1 = tk.LabelFrame(win, text="Модель A", padx=10, pady=10)
        frame1.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(frame1, text="Нейронов:").grid(row=0, column=0)
        entry_h1 = tk.Entry(frame1, width=5); entry_h1.insert(0, "8"); entry_h1.grid(row=0, column=1)
        tk.Label(frame1, text="Эпох:").grid(row=1, column=0)
        entry_e1 = tk.Entry(frame1, width=5); entry_e1.insert(0, "4000"); entry_e1.grid(row=1, column=1)
        frame2 = tk.LabelFrame(win, text="Модель B", padx=10, pady=10)
        frame2.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(frame2, text="Нейронов:").grid(row=0, column=0)
        entry_h2 = tk.Entry(frame2, width=5); entry_h2.insert(0, "16"); entry_h2.grid(row=0, column=1)
        tk.Label(frame2, text="Эпох:").grid(row=1, column=0)
        entry_e2 = tk.Entry(frame2, width=5); entry_e2.insert(0, "6000"); entry_e2.grid(row=1, column=1)
        result_text = tk.Text(win, wrap=tk.WORD, height=15)
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def run():
            try:
                h1 = int(entry_h1.get()); e1 = int(entry_e1.get())
                h2 = int(entry_h2.get()); e2 = int(entry_e2.get())
            except:
                messagebox.showerror("Ошибка", "Введите целые числа"); return
            result_text.delete(1.0, tk.END); result_text.insert(tk.END, "Обучение моделей...\n"); win.update()
            X_tr, X_te, Y_tr, Y_te = train_test_split(X_full, Y_full, test_size=0.2, random_state=42)
            nn1 = ExplainableNN(len(vocab), h1, lr=0.5); nn1.batch_train(X_tr, Y_tr, epochs=e1, lr=0.5, callback=lambda msg, e, l: None)
            nn2 = ExplainableNN(len(vocab), h2, lr=0.5); nn2.batch_train(X_tr, Y_tr, epochs=e2, lr=0.5, callback=lambda msg, e, l: None)
            pred1 = nn1.predict(X_te).flatten(); pred2 = nn2.predict(X_te).flatten()
            true = Y_te.flatten()
            acc1 = np.mean(pred1 == true); acc2 = np.mean(pred2 == true)
            result_text.insert(tk.END, f"Модель A ({h1} нейронов, {e1} эпох): точность {acc1:.1%}\n")
            result_text.insert(tk.END, f"Модель B ({h2} нейронов, {e2} эпох): точность {acc2:.1%}\n")
            if acc1 > acc2: result_text.insert(tk.END, "Победила модель A!\n")
            elif acc2 > acc1: result_text.insert(tk.END, "Победила модель B!\n")
            else: result_text.insert(tk.END, "Ничья!\n")
        tk.Button(win, text="Запустить турнир", command=run).pack(pady=5)

    def auto_tune(self):
        win = tk.Toplevel(self.window)
        win.title("Автоподбор параметров")
        win.geometry("600x400")
        tk.Label(win, text="Поиск лучшей комбинации нейронов и эпох...").pack(pady=10)
        text_area = tk.Text(win, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        def safe_insert(msg):
            try:
                text_area.insert(tk.END, msg + "\n")
                text_area.see(tk.END)
                win.update_idletasks()
            except: pass
        def worker():
            try:
                X_tr, X_val, Y_tr, Y_val = train_test_split(X_full, Y_full, test_size=0.2, random_state=42)
                best_acc, best_params = 0, None
                for hidden in [4, 8, 12, 16]:
                    for epochs in [2000, 4000, 6000]:
                        self.window.after(0, lambda h=hidden, e=epochs: safe_insert(f"Тестируем {h} нейронов, {e} эпох..."))
                        model = ExplainableNN(len(vocab), hidden, lr=0.5)
                        model.batch_train(X_tr, Y_tr, epochs=epochs, lr=0.5, callback=lambda msg, e, l: None)
                        acc = np.mean(model.predict(X_val).flatten() == Y_val.flatten())
                        self.window.after(0, lambda a=acc: safe_insert(f"  Точность: {a:.1%}"))
                        if acc > best_acc:
                            best_acc, best_params = acc, (hidden, epochs)
                self.window.after(0, lambda: safe_insert(f"\nЛучшая: {best_params[0]} нейронов, {best_params[1]} эпох, точность {best_acc:.1%}"))
                def ask():
                    if messagebox.askyesno("Автоподбор", "Установить лучшие параметры?"):
                        self.hidden_var.set(str(best_params[0]))
                        self.epochs_var.set(str(best_params[1]))
                self.window.after(0, ask)
                self.window.after(0, lambda: safe_insert("Готово."))
            except Exception as e:
                self.window.after(0, lambda: safe_insert(f"Ошибка: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def show_help(self):
        help_text = """Фуги Фуги ИИ – помощь

Эпохи – сколько раз нейросеть просматривает все примеры.
Нейронов – количество вычислительных элементов в скрытом слое.
Переобучить – запускает обучение с выбранными параметрами.
Логи – показывает ошибку на каждой 500-й эпохе.
График – визуализирует снижение ошибки.
Сохранить график – экспорт в PNG.
Блокнот – анализ целого текста (нескольких предложений).
Сочинялка – генерирует фразу на основе базы.
Эксперт – показывает влияние слов во фразе.
Турнир – сравнивает две модели на тестовой выборке.
Автоподбор – автоматически ищет лучшие параметры.
Сохранить/загрузить веса – экспорт/импорт обученной модели.
Случайный режим – делает веса случайными.
Режим рассуждения – подробное объяснение ответа.
Структура сети – рисует схему нейросети.
Сохранить/загрузить конфиг – сохраняет все настройки и веса."""
        win = tk.Toplevel(self.window)
        win.title("Справка")
        win.geometry("600x500")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Segoe UI", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)

    def save_weights(self):
        if nn is None:
            messagebox.showinfo("Сохранение", "Нейросеть не обучена.")
            return
        try:
            np.savez("ff_weights.npz", W1=nn.W1, b1=nn.b1, W2=nn.W2, b2=nn.b2)
            messagebox.showinfo("Сохранение", "Веса сохранены в ff_weights.npz")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_weights(self):
        global nn
        if not os.path.exists("ff_weights.npz"):
            messagebox.showinfo("Загрузка", "Файл ff_weights.npz не найден.")
            return
        try:
            data = np.load("ff_weights.npz")
            hidden_dim = data['W1'].shape[1]
            input_dim = data['W1'].shape[0]
            curr = list(self.hidden_combo.cget('values'))
            if str(hidden_dim) not in curr:
                curr.append(str(hidden_dim))
                self.hidden_combo.config(values=curr)
            self.hidden_var.set(str(hidden_dim))
            new_nn = ExplainableNN(input_dim, hidden_dim, lr=0.5)
            new_nn.W1 = data['W1']; new_nn.b1 = data['b1']; new_nn.W2 = data['W2']; new_nn.b2 = data['b2']
            nn = new_nn
            self.random_mode = False
            self.random_btn.config(text="🎲 Случайный режим", bg="SystemButtonFace")
            self.status_label.config(text=f"Загружены веса (нейронов: {hidden_dim})", fg="green")
            self.display_message("Система", f"Веса загружены (нейронов: {hidden_dim})", "info")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def toggle_random_mode(self):
        global nn
        if self.random_mode:
            if self.nn_trained is not None:
                nn = self.nn_trained
                self.random_mode = False
                self.random_btn.config(text="🎲 Случайный режим", bg="SystemButtonFace")
                if self.saved_epochs:
                    self.epochs_var.set(self.saved_epochs)
                    self.hidden_var.set(self.saved_hidden)
                self.status_label.config(text=f"Готово (эпох: {self.epochs_var.get()}, нейронов: {self.hidden_var.get()})", fg="green")
                self.display_message("Система", "Восстановлена обученная нейросеть.", "info")
            else:
                self.display_message("Система", "Нет сохранённой модели.", "info")
        else:
            if nn is None:
                self.display_message("Система", "Сначала обучите нейросеть.", "info")
                return
            self.nn_trained = nn
            self.saved_epochs = self.epochs_var.get()
            self.saved_hidden = self.hidden_var.get()
            ep_vals = list(self.epochs_combo.cget('values'))
            if "0" not in ep_vals:
                ep_vals.append("0")
                self.epochs_combo.config(values=ep_vals)
            hid_vals = list(self.hidden_combo.cget('values'))
            if "0" not in hid_vals:
                hid_vals.append("0")
                self.hidden_combo.config(values=hid_vals)
            self.epochs_var.set("0")
            self.hidden_var.set("0")
            input_dim = nn.W1.shape[0]
            hidden_dim = nn.W1.shape[1]
            random_nn = ExplainableNN(input_dim, hidden_dim, lr=0.5)
            random_nn.W1 = np.random.randn(input_dim, hidden_dim) * 0.5
            random_nn.b1 = np.zeros((1, hidden_dim))
            random_nn.W2 = np.random.randn(hidden_dim, 1) * 0.5
            random_nn.b2 = np.zeros((1, 1))
            nn = random_nn
            self.random_mode = True
            self.random_btn.config(text="🔁 Восстановить веса", bg="#ffcccc")
            self.status_label.config(text="Случайный режим: эпохи 0, нейроны 0", fg="red")
            self.display_message("Система", "Случайный режим: параметры обнулены, ответы случайны!", "info")

    def save_config(self):
        config = {
            "epochs": self.epochs_var.get(),
            "hidden": self.hidden_var.get(),
            "reasoning_mode": self.reasoning_var.get(),
            "dark_theme": getattr(self, 'dark_mode', False)
        }
        if nn is not None:
            buffer = io.BytesIO()
            np.savez(buffer, W1=nn.W1, b1=nn.b1, W2=nn.W2, b2=nn.b2)
            config["weights"] = base64.b64encode(buffer.getvalue()).decode('ascii')
        try:
            with open("ff_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Конфигурация", "Конфигурация сохранена в ff_config.json")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_config(self):
        if not os.path.exists("ff_config.json"):
            messagebox.showinfo("Конфигурация", "Файл ff_config.json не найден.")
            return
        try:
            with open("ff_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            self.epochs_var.set(config.get("epochs", "4000"))
            self.hidden_var.set(config.get("hidden", "8"))
            self.reasoning_var.set(config.get("reasoning_mode", False))
            if config.get("dark_theme", False) != getattr(self, 'dark_mode', False):
                self.toggle_nn_theme()
            if "weights" in config:
                data = base64.b64decode(config["weights"])
                loaded = np.load(io.BytesIO(data))
                input_dim = loaded['W1'].shape[0]
                hidden_dim = loaded['W1'].shape[1]
                new_nn = ExplainableNN(input_dim, hidden_dim, lr=0.5)
                new_nn.W1 = loaded['W1']; new_nn.b1 = loaded['b1']; new_nn.W2 = loaded['W2']; new_nn.b2 = loaded['b2']
                global nn
                nn = new_nn
                self.display_message("Система", "Загружены веса основной нейросети.", "info")
            messagebox.showinfo("Конфигурация", "Конфигурация загружена.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def visualize_network(self):
        if nn is None:
            messagebox.showinfo("Визуализация", "Нейросеть ещё не обучена.")
            return
        phrase = self.last_analyzed_phrase
        if not phrase:
            phrase = simpledialog.askstring("Визуализация", "Введите фразу (слова будут показаны на схеме):", parent=self.window)
            if not phrase:
                return
            phrase = phrase.strip().lower()
        words = phrase.split()
        if not words:
            messagebox.showinfo("Визуализация", "Фраза не содержит слов.")
            return
        display_words = words[:10]
        indices = []
        for w in display_words:
            if w in vocab:
                indices.append(vocab.index(w))
            else:
                indices.append(-1)
        win = tk.Toplevel(self.window)
        win.title("Структура сети (слова из фразы)")
        win.geometry("1200x800")
        canvas = tk.Canvas(win, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)
        input_neurons = len(display_words)
        hidden_neurons = nn.W1.shape[1]
        radius = 25
        x_start, y_start = 120, 80
        x_step, y_step = 250, 60
        input_pos = [(x_start, y_start + i * y_step) for i in range(input_neurons)]
        hidden_pos = [(x_start + x_step, y_start + i * y_step) for i in range(hidden_neurons)]
        output_pos = [(x_start + 2 * x_step, y_start + (hidden_neurons - 1) * y_step // 2)]
        for i, (ix, iy) in enumerate(input_pos):
            idx = indices[i]
            if idx == -1: continue
            for j, (hx, hy) in enumerate(hidden_pos):
                w = nn.W1[idx, j]
                color = "green" if w > 0 else "red"
                width = min(5, max(1, int(abs(w) * 3)))
                canvas.create_line(ix + radius, iy, hx - radius, hy, fill=color, width=width)
        for j, (hx, hy) in enumerate(hidden_pos):
            w = nn.W2[j, 0]
            color = "green" if w > 0 else "red"
            width = min(5, max(1, int(abs(w) * 3)))
            canvas.create_line(hx + radius, hy, output_pos[0][0] - radius, output_pos[0][1], fill=color, width=width)
        for i, (x, y) in enumerate(input_pos):
            canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="lightblue", outline="black")
            word = display_words[i] if i < len(display_words) else ""
            display = word if len(word) <= 8 else word[:7] + "."
            canvas.create_text(x, y, text=display, font=("Arial", 8))
        for (x, y) in hidden_pos:
            canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="lightgreen", outline="black")
            canvas.create_text(x, y, text="H", font=("Arial", 10))
        for (x, y) in output_pos:
            canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="lightcoral", outline="black")
            canvas.create_text(x, y, text="Out", font=("Arial", 10))
        leg_x = x_start + 2 * x_step + 80
        leg_y = y_start
        canvas.create_text(leg_x, leg_y, text="Легенда:", anchor="w", font=("Arial", 10))
        canvas.create_line(leg_x, leg_y + 20, leg_x + 30, leg_y + 20, fill="green", width=2)
        canvas.create_text(leg_x + 35, leg_y + 20, text="Положительный вес", anchor="w", font=("Arial", 9))
        canvas.create_line(leg_x, leg_y + 40, leg_x + 30, leg_y + 40, fill="red", width=2)
        canvas.create_text(leg_x + 35, leg_y + 40, text="Отрицательный вес", anchor="w", font=("Arial", 9))
        canvas.create_text(leg_x, leg_y + 60, text="Толщина линии = |вес|", anchor="w", font=("Arial", 9))

    def get_reasoning_text(self, phrase, vec, raw, guess, confidence):
        words = phrase.split()
        if not words:
            return "Нет слов для анализа."
        contributions = []
        for w in words:
            if w in vocab:
                idx = vocab.index(w)
                contrib = np.sum(nn.W1[idx, :] * nn.W2[:, 0])
                contributions.append((w, contrib))
            else:
                contributions.append((w, 0.0))
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        text = "🧠 **Режим рассуждения:**\n"
        text += f"Фраза: «{phrase}»\nСлова: {', '.join(words)}\n"
        text += "Влияние слов (самые сильные):\n"
        for w, c in contributions[:5]:
            effect = "положительное" if c > 0 else "отрицательное"
            text += f"  • «{w}» → {effect} (сила {abs(c):.3f})\n"
        text += f"Итоговый сигнал: {raw:.3f} → {'позитив' if guess == 1 else 'негатив'} (уверенность {confidence:.0%})"
        return text

    def on_key_release(self, event):
        text = self.input_entry.get()
        if not text:
            self.autocomplete_listbox.place_forget()
            return
        suggestions = get_autocomplete_options(text)
        if suggestions:
            self.autocomplete_listbox.delete(0, tk.END)
            for s in suggestions:
                self.autocomplete_listbox.insert(tk.END, s)
            x = self.input_entry.winfo_rootx() - self.window.winfo_rootx()
            y = self.input_entry.winfo_rooty() - self.window.winfo_rooty() + self.input_entry.winfo_height()
            self.autocomplete_listbox.place(x=x, y=y, width=self.input_entry.winfo_width())
        else:
            self.autocomplete_listbox.place_forget()

    def on_autocomplete_select(self, event):
        selection = self.autocomplete_listbox.curselection()
        if selection:
            chosen = self.autocomplete_listbox.get(selection[0])
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, chosen)
            self.autocomplete_listbox.place_forget()
            self.input_entry.focus_set()

    def show_feedback_panel(self):
        if self.feedback_frame:
            self.hide_feedback_panel()
        self.feedback_frame = tk.Frame(self.window, bg="#f0f0f0", pady=5)
        self.feedback_frame.pack(fill=tk.X, before=self.input_frame)
        like_btn = tk.Button(self.feedback_frame, text="👍", command=self.like_feedback, width=3)
        like_btn.pack(side=tk.LEFT, padx=10, pady=2)
        dislike_btn = tk.Button(self.feedback_frame, text="👎", command=self.dislike_feedback, width=3)
        dislike_btn.pack(side=tk.LEFT, padx=10, pady=2)
        close_btn = tk.Button(self.feedback_frame, text="✖", command=self.hide_feedback_panel, width=2, bg="#ffcccc")
        close_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        self.timer_label = tk.Label(self.feedback_frame, text="⏱️ 8с", bg="#f0f0f0", font=("Arial", 9))
        self.timer_label.pack(side=tk.RIGHT, padx=10)
        self.feedback_remaining = 8
        self.update_feedback_timer()

    def hide_feedback_panel(self):
        if self.feedback_timer_id:
            self.window.after_cancel(self.feedback_timer_id)
            self.feedback_timer_id = None
        if self.feedback_frame:
            self.feedback_frame.destroy()
            self.feedback_frame = None

    def update_feedback_timer(self):
        if not self.feedback_frame:
            return
        if self.feedback_remaining <= 0:
            self.hide_feedback_panel()
            return
        self.timer_label.config(text=f"⏱️ {self.feedback_remaining}с")
        self.feedback_remaining -= 1
        self.feedback_timer_id = self.window.after(1000, self.update_feedback_timer)

    def like_feedback(self):
        if self.last_user_text:
            if self.last_user_text not in history:
                history[self.last_user_text] = self.last_guess
                save_history(history)
                self.display_message("Система", "Спасибо за лайк! Запомнил.", "info")
            else:
                self.display_message("Система", "Эта фраза уже есть в базе.", "info")
        self.hide_feedback_panel()

    def dislike_feedback(self):
        win = tk.Toplevel(self.window)
        win.title("Исправление оценки")
        win.geometry("300x150")
        win.transient(self.window)
        win.grab_set()
        win.resizable(False, False)
        tk.Label(win, text=f"Фраза: {self.last_user_text}", wraplength=280).pack(pady=5)
        tk.Label(win, text="Правильная оценка (1=позитив, 0=негатив):").pack()
        entry = tk.Entry(win)
        entry.pack(pady=5)
        def submit():
            try:
                real = int(entry.get())
                if real in (0,1):
                    history[self.last_user_text] = real
                    save_history(history)
                    nn.online_step(self.last_vec, real, lr=0.3)
                    self.display_message("Система", f"Спасибо! Исправлено на {['негатив','позитив'][real]}.", "info")
                    win.destroy()
                    self.hide_feedback_panel()
                else:
                    messagebox.showerror("Ошибка", "Введите 0 или 1")
            except:
                messagebox.showerror("Ошибка", "Введите число 0 или 1")
        tk.Button(win, text="Отправить", command=submit).pack(pady=10)

    def process_input(self, event=None):
        self.hide_feedback_panel()
        if nn is None:
            self.display_message("Система", "Нейросеть ещё не обучена.", "info")
            return
        user_text = self.input_entry.get().strip().lower()
        if not user_text:
            return
        self.last_analyzed_phrase = user_text
        self.input_entry.delete(0, tk.END)
        self.autocomplete_listbox.place_forget()
        self.display_message("Вы", user_text, "user")

        vec = vectorize(user_text)
        raw = nn.predict_raw(vec.reshape(1, -1))[0][0]
        boosted = apply_exclamation_boost(user_text, raw)
        guess = 1 if boosted > 0.5 else 0
        sentiment = "позитив" if guess == 1 else "негатив"
        confidence = boosted if boosted > 0.5 else 1 - boosted
        reply = f"Я думаю, это {sentiment} (уверенность {confidence:.0%})."
        if user_text.endswith('!'):
            reply += " Восклицание усилило мою уверенность!"
        if self.reasoning_var.get():
            reasoning = self.get_reasoning_text(user_text, vec, raw, guess, confidence)
            reply += f"\n\n{reasoning}"

        self.display_message("Фуги Фуги ИИ", reply, "assistant")
        self.last_user_text = user_text
        self.last_vec = vec
        self.last_guess = guess
        self.last_raw = raw
        self.show_feedback_panel()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = SentimentApp(root, None)
    root.mainloop()