import requests
import re
import os

# Прямая ссылка на готовый файл с диалогами (реально рабочий датасет)
# Это открытый датасет с Hugging Face, но мы берём уже обработанную версию
URL = "https://raw.githubusercontent.com/RussianNLP/CoAT/main/data/train.txt"

def download_file(url, filename):
    print(f"⬇️ Загрузка {filename}...")
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"Ошибка: не удалось загрузить файл (статус {response.status_code})")
        return False
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192
    with open(filename, 'wb') as f:
        for data in response.iter_content(block_size):
            f.write(data)
    print(f"✅ Файл {filename} загружен. Размер: {total_size} байт.")
    return True

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^а-яёa-z0-9 .,!?]', '', text)
    return text.strip()

if not os.path.exists("dialogue_data.txt"):
    print("Скачивание датасета...")
    success = download_file(URL, "temp_data.txt")
    if not success:
        print("❌ Не удалось скачать файл. Попробуй запустить позже.")
        exit()
else:
    print("Файл dialogue_data.txt уже существует. Пропускаем скачивание.")

all_sentences = []
print("Обработка данных...")
with open("temp_data.txt", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i % 1000 == 0 and i > 0:
            print(f"Обработано {i} строк, собрано {len(all_sentences)} предложений")
        if i >= 10000:  # возьмём первые 10000 строк для скорости
            break
        cleaned = clean_text(line)
        if len(cleaned.split()) >= 5:
            all_sentences.append(cleaned)

print(f"Всего собрано {len(all_sentences)} предложений.")
with open("dialogue_data.txt", "w", encoding="utf-8") as f:
    for sent in all_sentences:
        f.write(sent + "\n")

# Удаляем временный файл
if os.path.exists("temp_data.txt"):
    os.remove("temp_data.txt")

print("✅ Готово! Файл dialogue_data.txt создан.")
print(f"Размер: {len(all_sentences)} предложений.")