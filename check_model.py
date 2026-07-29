import pickle
import numpy as np

with open("big_nn_model.pkl", "rb") as f:
    w = pickle.load(f)

for key in w:
    print(f"{key}: shape={w[key].shape}, dtype={w[key].dtype}")
    # Покажем первые 5 значений (если массив не слишком большой)
    flat = w[key].flatten()
    print(f"    первые 5 значений: {flat[:5]}")