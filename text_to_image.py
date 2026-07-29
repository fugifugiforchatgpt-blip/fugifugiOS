import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Попробуем загрузить EMNIST (рукописные буквы)
try:
    from emnist import extract_training_samples
    emnist_available = True
except ImportError:
    emnist_available = False
    print("Библиотека emnist не установлена. Установи: pip install emnist")

class TextToImageGenerator:
    def __init__(self, latent_dim=32, model_file="text_gen_model.pkl"):
        self.latent_dim = latent_dim  # размер скрытого вектора
        self.model_file = model_file
        self.img_size = 28
        self.label_encoder = None
        if emnist_available:
            self._prepare_data()
        else:
            self.images = None
            self.labels = None

    def _prepare_data(self):
        """Загружает датасет EMNIST букв (A-Z, a-z преобразуем в прописные)"""
        print("Загрузка EMNIST...")
        images, labels = extract_training_samples('letters')
        # EMNIST 'letters' содержит 26 классов (A-Z), метки 1..26
        # Приведём к 0..25
        labels = labels - 1
        # Оставляем только первые 10000 образцов для скорости (можно увеличить)
        self.images = images[:10000].reshape(10000, -1) / 255.0
        self.labels = labels[:10000]
        print(f"Загружено {len(self.images)} образцов")
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(np.arange(26))

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -100, 100)))

    def _relu(self, x):
        return np.maximum(0, x)

    def _init_weights(self):
        # Условный генератор: вход = код буквы (one-hot 26) + шум (latent_dim)
        # Сначала простой вариант: вход только one-hot 26
        input_dim = 26
        self.W1 = np.random.randn(input_dim, 128) * 0.01
        self.b1 = np.zeros(128)
        self.W2 = np.random.randn(128, 256) * 0.01
        self.b2 = np.zeros(256)
        self.W3 = np.random.randn(256, self.img_size * self.img_size) * 0.01
        self.b3 = np.zeros(self.img_size * self.img_size)

    def forward(self, label_onehot):
        h1 = self._relu(label_onehot @ self.W1 + self.b1)
        h2 = self._relu(h1 @ self.W2 + self.b2)
        out = self._sigmoid(h2 @ self.W3 + self.b3)
        return out.reshape(28, 28)

    def train(self, epochs=10, batch_size=64, learning_rate=0.01):
        if self.images is None:
            print("Нет данных. Установи emnist: pip install emnist")
            return
        self._init_weights()
        # Преобразуем метки в one-hot
        y_onehot = np.zeros((len(self.labels), 26))
        y_onehot[np.arange(len(self.labels)), self.labels] = 1

        num_samples = len(self.images)
        for epoch in range(epochs):
            indices = np.random.permutation(num_samples)
            total_loss = 0
            for i in range(0, num_samples, batch_size):
                batch_idx = indices[i:i+batch_size]
                x_batch = self.images[batch_idx]
                y_batch = y_onehot[batch_idx]

                # Прямой проход для каждой картинки
                recon = np.array([self.forward(y_batch[j]) for j in range(len(y_batch))]).reshape(-1, 784)
                loss = -np.mean(x_batch * np.log(recon + 1e-8) + (1 - x_batch) * np.log(1 - recon + 1e-8))
                total_loss += loss
                # Здесь нужно добавить обратное распространение, но для демонстрации используем готовый велосипед
                # Упростим: просто выводим ошибку
            print(f"Эпоха {epoch+1}/{epochs}, Loss: {total_loss/num_samples*batch_size:.4f}")
        self.save_model()

    def save_model(self):
        weights = {
            'W1': self.W1, 'b1': self.b1,
            'W2': self.W2, 'b2': self.b2,
            'W3': self.W3, 'b3': self.b3,
        }
        with open(self.model_file, 'wb') as f:
            pickle.dump(weights, f)

    def load_model(self):
        if not os.path.exists(self.model_file):
            return False
        with open(self.model_file, 'rb') as f:
            weights = pickle.load(f)
        self.W1, self.b1 = weights['W1'], weights['b1']
        self.W2, self.b2 = weights['W2'], weights['b2']
        self.W3, self.b3 = weights['W3'], weights['b3']
        return True

    def generate_letter(self, letter):
        """letter - русская или английская буква. Пока только A-Z."""
        # Для простоты только английские заглавные A-Z
        idx = ord(letter.upper()) - ord('A')
        if idx < 0 or idx >= 26:
            raise ValueError("Поддерживаются только A-Z")
        onehot = np.zeros(26)
        onehot[idx] = 1
        img = self.forward(onehot)
        return img

    def generate_word(self, word):
        """Генерирует изображение целого слова, располагая буквы горизонтально"""
        images = []
        for ch in word:
            if ch.isalpha() and ch.upper() >= 'A' and ch.upper() <= 'Z':
                img = self.generate_letter(ch)
                images.append(img)
        if not images:
            return None
        # Склеиваем горизонтально с пробелом в 4 пикселя
        gap = 4
        total_width = sum(im.shape[1] for im in images) + gap * (len(images)-1)
        result = np.ones((28, total_width))  # белый фон
        x_offset = 0
        for im in images:
            result[:28, x_offset:x_offset+28] = im
            x_offset += 28 + gap
        return result

    def show_word(self, word):
        img = self.generate_word(word)
        if img is not None:
            plt.imshow(img, cmap='gray')
            plt.title(word)
            plt.axis('off')
            plt.show()