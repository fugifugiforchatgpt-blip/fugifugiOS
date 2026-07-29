import numpy as np
from big_nn import BigNeuralNetwork
from sklearn.datasets import fetch_openml

nn = BigNeuralNetwork()
mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='liac-arff')
X = mnist.data.astype(np.float32) / 255.0
y = mnist.target.astype(int)

for i in range(5):
    img = X[i]
    pred = nn.predict_one(img)
    print(f"Правильная цифра: {y[i]}, предсказание: {pred}")