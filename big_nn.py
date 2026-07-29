import numpy as np
import pickle
import os
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split

class BigNeuralNetwork:
    def __init__(self, model_file="big_nn_model.pkl"):
        self.model_file = model_file
        if os.path.exists(model_file):
            self._load()
            print("Модель загружена из файла.")
        else:
            print("Обучение нейросети (1 минута)...")
            self._train()
            self._save()

    def _train(self):
        print("Загрузка MNIST...")
        mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='liac-arff')
        X = mnist.data.astype(np.float32) / 255.0
        y = mnist.target.astype(int)
        # Для скорости возьмём 20000 картинок (можно больше)
        X = X[:20000]
        y = y[:20000]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # Нейросеть: 2 скрытых слоя (256 и 128 нейронов)
        self.clf = MLPClassifier(hidden_layer_sizes=(256, 128), max_iter=10, batch_size=128, verbose=True, random_state=42)
        self.clf.fit(X_train, y_train)
        acc = self.clf.score(X_test, y_test)
        print(f"Точность на тесте: {acc:.2%}")

    def predict_one(self, img):
        if img.ndim == 2:
            img = img.flatten()
        img = img.reshape(1, -1)
        return self.clf.predict(img)[0]

    def _save(self):
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.clf, f)

    def _load(self):
        with open(self.model_file, 'rb') as f:
            self.clf = pickle.load(f)

if __name__ == "__main__":
    nn = BigNeuralNetwork()
    # Тест на первых 5 картинках
    from sklearn.datasets import fetch_openml
    mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='liac-arff')
    X = mnist.data.astype(np.float32) / 255.0
    y = mnist.target.astype(int)
    for i in range(5):
        pred = nn.predict_one(X[i])
        print(f"Правильная: {y[i]}, предсказание: {pred}")