import json
import csv
import re

with open("yandex_reviews.json", 'r') as file:
    data = json.load(file)
    found_court = ""
    court_reviews = []
    max_reviews = 0
    for court in data:
        if len(data[court]) > max_reviews:
            max_reviews = len(data[court])
            court_reviews = data[court]
            found_court = court

new_data = []
for i in court_reviews:
    cleaned_text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9\s.,!?-]', '', i["text"])
    new_data.append([cleaned_text])  # Каждый отзыв - отдельный список

# Записываем без пустых строк
with open("max_reviews.csv", 'w', newline='') as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerows(new_data)
