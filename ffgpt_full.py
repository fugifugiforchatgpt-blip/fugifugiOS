import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import random
import os
import pickle
import re
import numpy as np
from collections import Counter
from PIL import ImageTk
from ff_gpt_photos import generate_object_image

# ============================
# 1. ЗАГРУЗКА ДАННЫХ (из файла или встроенных)
# ============================

def load_texts_from_file(filename):
    """Загружает предложения из текстового файла (по одному на строку)"""
    if not os.path.exists(filename):
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        texts = [line.strip() for line in lines if line.strip()]
    return texts

# ============================
# 1. МОЙ СОБСТВЕННЫЙ ДАТАСЕТ (вставь сюда свои фразы)
# ============================

# ============================
# 1. ГЕНЕРАЦИЯ МОЕГО ДАТАСЕТА
# ============================

sample_texts = []

subjects = [
    "Я","Ты","Он","Она","Мы","Они",
    "Программист","Студент","Учитель","Кот","Собака",
    "Робот","Нейросеть","Компьютер","Пользователь",
    "Инженер","Доктор","Художник","Музыкант","Повар",
    "Водитель","Пилот","Школьник","Геймер","Блогер",
    "Учёный","Полицейский","Пожарный","Космонавт","Фермер",
    "Мама","Папа","Друг","Подруга","Ребёнок",
    "Разработчик","Администратор","Дизайнер","Телефон",
    "Ноутбук","ИИ","ФФGPT","Ассистент","Человек",
    "Minecraft","Сервер","Игрок","Автомобиль","Дрон"
]

verbs = [
    "читает","пишет","изучает","создаёт","анализирует",
    "запускает","проверяет","обновляет","тестирует",
    "использует","разрабатывает","исследует",
    "рисует","строит","ремонтирует","скачивает",
    "открывает","закрывает","копирует","удаляет",
    "сохраняет","покупает","продаёт","объясняет",
    "отвечает","разговаривает","играет","готовит",
    "путешествует","смотрит","слушает","печатает",
    "учится","помогает","ищет","находит",
    "решает","программирует","запоминает","обрабатывает",
    "сравнивает","рисует","улучшает","загружает",
    "вычисляет","обучает","обучается","собирает",
    "передаёт","отправляет"
]

objects = [
    "код","проект","программу","модель","алгоритм",
    "датасет","сервер","файл","документ","систему",
    "базу данных","искусственный интеллект","телефон",
    "компьютер","ноутбук","игру","сайт",
    "приложение","видео","музыку","картинку",
    "дом","машину","дерево","книгу",
    "задачу","нейросеть","чат","бота",
    "камеру","окно","клавиатуру","мышь",
    "процессор","экран","монитор","дорогу",
    "робота","корабль","самолёт","ракету",
    "космос","планету","карту","интернет",
    "Wi-Fi","Bluetooth","диск","операционную систему"
]

places = [
    "дома","в офисе","в университете","в интернете",
    "на сервере","в лаборатории","в школе",
    "на улице","в магазине","в парке",
    "в библиотеке","в машине","в самолёте",
    "на кухне","в комнате","в гараже",
    "на работе","на уроке","в городе",
    "на даче","на заводе","в космосе",
    "на орбите","в лесу","на пляже",
    "в метро","в поезде","в больнице",
    "в музее","в замке"
]

adjectives = [
    "большой","маленький","новый","старый","умный",
    "быстрый","медленный","сильный","слабый","красивый",
    "интересный","полезный","современный","мощный",
    "яркий","тихий","громкий","надёжный","сложный",
    "простой","зелёный","синий","красный","чёрный",
    "белый","круглый","квадратный","цифровой","реальный"
]

templates = [
    "{subject} {verb} {object} {place}.",
    "{subject} быстро {verb} {object}.",
    "{subject} медленно {verb} {object}.",
    "{subject} хочет {verb} {object}.",
    "{subject} может {verb} {object}.",
    "{subject} любит {object}.",
    "{subject} не любит {object}.",
    "{subject} часто {verb} {object}.",
    "{subject} редко {verb} {object}.",
    "{subject} всегда {verb} {object}.",
    "{subject} никогда не {verb} {object}.",
    "{subject} вчера {verb} {object}.",
    "{subject} сегодня {verb} {object}.",
    "{subject} завтра будет {verb} {object}.",
    "{subject} использует {adjective} {object}.",
    "{subject} создаёт {adjective} {object}.",
    "{subject} нашёл {adjective} {object}.",
    "{subject} потерял {adjective} {object}.",
    "{subject} изучает {adjective} {object} {place}.",
    "{subject} программирует {object} {place}."
]

sample_texts = []

for template in templates:
    for subject in subjects:
        for verb in verbs:
            for obj in objects:
                for place in places:
                    adjective = random.choice(adjectives)

                    sample_texts.append(
                        template.format(
                            subject=subject,
                            verb=verb,
                            object=obj,
                            place=place,
                            adjective=adjective
                        )
                    )

                    # Ограничиваем размер датасета
                    if len(sample_texts) >= 200000:
                        break
                if len(sample_texts) >= 200000:
                    break
            if len(sample_texts) >= 200000:
                break
        if len(sample_texts) >= 200000:
            break
    if len(sample_texts) >= 200000:
        break

random.shuffle(sample_texts)
print(f"✅ Сгенерировано {len(sample_texts)} предложений")

# ============================
# 2. ОЧИСТКА И ПОДГОТОВКА ДАННЫХ
# ============================

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^а-яёa-z0-9 ]', '', text)
    return text.strip()

cleaned_texts = [clean_text(t) for t in sample_texts if t.strip()]
print(f"✅ Очищено {len(cleaned_texts)} предложений")

# ============================
# 3. ТОКЕНИЗАЦИЯ И СОЗДАНИЕ СЛОВАРЯ
# ============================

def tokenize(text):
    return text.split()

all_tokens = []
for text in cleaned_texts:
    all_tokens.extend(tokenize(text))

word_counts = Counter(all_tokens)
vocab = sorted(word_counts.keys())
word2idx = {word: idx + 1 for idx, word in enumerate(vocab)}
word2idx['<UNK>'] = 0
idx2word = {idx: word for word, idx in word2idx.items()}
vocab_size = len(vocab) + 1

print(f"📖 Размер словаря: {vocab_size} слов")

def encode_text(text):
    tokens = tokenize(text)
    return [word2idx.get(token, 0) for token in tokens]

encoded_texts = [encode_text(text) for text in cleaned_texts]

# ============================
# 4. ПОДГОТОВКА ДАННЫХ ДЛЯ ОБУЧЕНИЯ
# ============================

SEQ_LENGTH = 3

def create_sequences(encoded_texts, seq_length):
    X, y = [], []
    for seq in encoded_texts:
        if len(seq) > seq_length:
            for i in range(len(seq) - seq_length):
                X.append(seq[i:i + seq_length])
                y.append(seq[i + seq_length])
    return np.array(X, dtype=np.int64), np.array(y, dtype=np.int64)

X, y = create_sequences(encoded_texts, SEQ_LENGTH)
print(f"📊 Создано {len(X)} обучающих примеров")

if len(X) == 0:
    print("⚠️ Нет данных для обучения! Уменьши SEQ_LENGTH.")
    # Если данных нет, создадим хотя бы один пример для теста
    X = np.array([[0, 0, 0]])
    y = np.array([0])

# ============================
# 5. ОБУЧЕНИЕ МОДЕЛИ (MLP)
# ============================

try:
    from sklearn.neural_network import MLPClassifier
except ImportError:
    print("❌ Установи scikit-learn: pip install scikit-learn")
    exit()

MODEL_FILE = "ffgpt_model.pkl"

X_flat = X.reshape(X.shape[0], -1)

if os.path.exists(MODEL_FILE):
    print("📂 Загружаю готовую модель...")

    with open(MODEL_FILE, "rb") as f:
        data = pickle.load(f)

    model = data["model"]
    word2idx = data["word2idx"]
    idx2word = data["idx2word"]

    print("✅ Модель успешно загружена!")

else:
    print("🧠 Обучаю модель...")

    model = MLPClassifier(
        hidden_layer_sizes=(48, 24),
        max_iter=80,
        random_state=42,
        verbose=True,
        early_stopping=True
    )

    model.fit(X_flat, y)

    print("💾 Сохраняю модель...")

    with open(MODEL_FILE, "wb") as f:
        pickle.dump({
            "model": model,
            "word2idx": word2idx,
            "idx2word": idx2word
        }, f)

    print("✅ Модель сохранена!")
print("✅ Обучение завершено!")

# ============================
# 6. СОХРАНЕНИЕ МОДЕЛИ
# ============================

with open('vocab.pkl', 'wb') as f:
    pickle.dump({
        'model': model,
        'word2idx': word2idx,
        'idx2word': idx2word
    }, f)
print("💾 Модель сохранена в vocab.pkl")

# ============================
# 7. ФУНКЦИИ ГЕНЕРАЦИИ ТЕКСТА
# ============================

def predict_next(tokens):
    """Предсказывает следующее слово"""
    if len(tokens) < SEQ_LENGTH:
        tokens = ['<UNK>'] * (SEQ_LENGTH - len(tokens)) + tokens
    seq = [word2idx.get(t, 0) for t in tokens[-SEQ_LENGTH:]]
    seq_flat = np.array(seq).reshape(1, -1)
    pred = model.predict(seq_flat)[0]
    return idx2word.get(pred, '<UNK>')

def generate_text_response(user_input, max_words=15):
    """Генерирует ответ на введённый текст"""
    words = user_input.lower().split()
    if not words:
        return "Скажи что-нибудь!"

    generated = words[:]
    for _ in range(max_words):
        next_word = predict_next(generated)
        if next_word == '<UNK>' or len(generated) > 100:
            break
        generated.append(next_word)

    response = ' '.join(generated)
    response = response.capitalize()
    if not response.endswith('.') and not response.endswith('!'):
        response += '.'
    return response

# ============================
# 8. ГРАФИЧЕСКИЙ ИНТЕРФЕЙС
# ============================

class FFChat:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 ФФGPT v0.5 (диалог + картинки)")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        self.root.configure(bg="#1a1a2e")

        self.is_generating = False
        self.images = []

        # Заголовок
        header = tk.Label(root, text="🧠 ФФGPT v0.5 (диалог + картинки)", 
                          font=("Arial", 20, "bold"), bg="#1a1a2e", fg="#e94560")
        header.pack(pady=10)

        # Статус
        status_text = f"✅ Модель загружена. Данных: {len(sample_texts)} предложений"
        self.status_label = tk.Label(root, text=status_text, bg="#1a1a2e", fg="#888888")
        self.status_label.pack(pady=2)

        # Область чата
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled',
                                                    font=("Segoe UI", 12), bg="#16213e",
                                                    fg="#f0f0f0", insertbackground="white",
                                                    bd=0, padx=15, pady=15)
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        self.chat_area.tag_config("user", foreground="#4caf50", font=("Segoe UI", 12, "bold"))
        self.chat_area.tag_config("assistant", foreground="#00d2ff", font=("Segoe UI", 12, "bold"))
        self.chat_area.tag_config("system", foreground="#ff9800", font=("Segoe UI", 11, "italic"))

        # Нижняя панель
        input_frame = tk.Frame(root, bg="#1a1a2e")
        input_frame.pack(fill=tk.X, padx=15, pady=10)

        self.input_field = tk.Entry(input_frame, font=("Segoe UI", 13),
                                    bg="#0f3460", fg="white", insertbackground="white",
                                    bd=0, highlightthickness=0, relief=tk.FLAT)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12)
        self.input_field.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(input_frame, text="Отправить", command=self.send_message,
                                  font=("Arial", 12, "bold"), bg="#e94560", fg="white",
                                  activebackground="#c73652", bd=0, padx=25, cursor="hand2")
        self.send_btn.pack(side=tk.RIGHT, padx=5)

        # Кнопки управления
        control_frame = tk.Frame(root, bg="#1a1a2e")
        control_frame.pack(pady=5)

        btn_clear = tk.Button(control_frame, text="Очистить чат", command=self.clear_chat,
                              bg="#0f3460", fg="white", font=("Arial", 10), bd=0, padx=15, cursor="hand2")
        btn_clear.pack(side=tk.LEFT, padx=5)

        btn_help = tk.Button(control_frame, text="Помощь", command=self.show_help,
                             bg="#0f3460", fg="white", font=("Arial", 10), bd=0, padx=15, cursor="hand2")
        btn_help.pack(side=tk.LEFT, padx=5)

        btn_exit = tk.Button(control_frame, text="Выход", command=self.root.destroy,
                             bg="#533483", fg="white", font=("Arial", 10), bd=0, padx=15, cursor="hand2")
        btn_exit.pack(side=tk.LEFT, padx=5)

        self.display_message("ФФGPT", f"Привет! Я умею общаться и рисовать. Данных: {len(sample_texts)} предложений.", "assistant")

    def display_message(self, sender, message, msg_type):
        self.chat_area.config(state='normal')
        tag = "user" if msg_type == "user" else "assistant" if msg_type == "assistant" else "system"
        self.chat_area.insert(tk.END, f"{sender}: ", tag)
        self.chat_area.insert(tk.END, f"{message}\n\n", "normal")
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def send_message(self, event=None):
        if self.is_generating:
            return

        user_input = self.input_field.get().strip()
        if not user_input:
            return
        self.input_field.delete(0, tk.END)

        self.display_message("Вы", user_input, "user")

        # Проверяем, запрос на картинку
        if "нарисуй" in user_input.lower():
            prompt = user_input.lower().replace("нарисуй", "").strip()
            if prompt:
                self.generate_image(prompt)
            else:
                self.display_message("ФФGPT", "Что именно нарисовать? Напиши, например: 'нарисуй дом'.", "assistant")
        else:
            # Текстовый ответ
            response = generate_text_response(user_input)
            self.display_message("ФФGPT", response, "assistant")

    def generate_image(self, prompt):
        self.is_generating = True
        self.send_btn.config(state=tk.DISABLED)
        self.display_message("ФФGPT", f"🎨 Рисую: {prompt}...", "assistant")
        try:
            img = generate_object_image(prompt)
            filename = f"ff_object_{random.randint(1000,9999)}.png"
            img.save(filename)
            self.display_message("ФФGPT", f"✅ Картинка сохранена: {filename}", "assistant")
            # Показываем миниатюру
            try:
                img_tk = ImageTk.PhotoImage(img.resize((200, 200)))
                self.chat_area.image_create(tk.END, image=img_tk)
                self.chat_area.insert(tk.END, "\n\n")
                if not hasattr(self, 'images'):
                    self.images = []
                self.images.append(img_tk)
            except:
                pass
        except Exception as e:
            self.display_message("ФФGPT", f"❌ Ошибка: {e}", "assistant")
        self.is_generating = False
        self.send_btn.config(state=tk.NORMAL)

    def clear_chat(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state='disabled')
        self.display_message("Система", "Чат очищен.", "system")
        if hasattr(self, 'images'):
            self.images.clear()

    def show_help(self):
        help_text = """ФФGPT v0.5 — Чат + Генератор картинок

Команды:
• Текст: просто напиши сообщение
• Картинка: нарисуй [объект]

Доступные объекты:
дом, дерево, солнце, облако, звезда, сердце, цветок, птица, рыба, корабль, ракета, луна, яблоко, банан, апельсин, арбуз, клубника, вишня, торт, мороженое, капкейк, пончик, пицца, бургер, картошка фри, хотдог, сэндвич, салат, суп, паста, рис, борщ, пельмени, вареники, блин, омлет, йогурт, кефир, творог, сметана, масло, хлеб, сыр, яйцо, бекон

и другие..."""
        messagebox.showinfo("Помощь", help_text)

# ============================
# 9. ЗАПУСК
# ============================

if __name__ == "__main__":
    root = tk.Tk()
    app = FFChat(root)
    root.mainloop()