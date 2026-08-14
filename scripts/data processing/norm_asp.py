import json
import re
import pymorphy3

# Инициализация морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

def normalize_word(word):
    """
    Приводит слово к нормальной форме (именительный падеж, единственное число)
    """
    # Очищаем слово от лишних символов
    word = re.sub(r'[^a-zA-Zа-яА-ЯёЁ]', '', word.lower())
    
    if not word:
        return word
    
    # Анализируем слово
    parsed = morph.parse(word)[0]
    
    # Приводим к нормальной форме
    normalized = parsed.normal_form
    
    return normalized

def normalize_aspects_list(aspects_list):
    """
    Нормализует список аспектов
    """
    normalized_aspects = []
    for word in aspects_list:
        # Очищаем и нормализуем каждое слово
        cleaned = re.sub(r'[^a-zA-Zа-яА-ЯёЁ]', '', word.lower())
        if cleaned:
            normalized = normalize_word(cleaned)
            normalized_aspects.append(normalized)
    return normalized_aspects

# Загрузка и обработка аспектов
aspects = []

with open('yandex_aspects.json', 'r', encoding='utf-8') as file:
    d = json.load(file)
    for court in d:
        for asp in range(len(d[court])):
            for word in d[court][asp]:
                # Очищаем слово
                cleaned = re.sub(r'[^a-zA-Zа-яА-ЯёЁ]', '', word.lower())
                if cleaned:
                    aspects.append(cleaned)

with open('google_aspects.json', 'r', encoding='utf-8') as file:
    d = json.load(file)
    for court in d:
        for asp in range(0, len(d[court])):
            for word in d[court][asp]:
                # Очищаем слово
                cleaned = re.sub(r'[^a-zA-Zа-яА-ЯёЁ]', '', word.lower())
                if cleaned:
                    aspects.append(cleaned)

# Нормализация всех аспектов
print("Нормализация аспектов...")
normalized_aspects = []
for aspect in aspects:
    norm_aspect = normalize_word(aspect)
    if norm_aspect:
        normalized_aspects.append(norm_aspect)

# Словарь тем (ключевые слова уже должны быть в нормальной форме)
themes = {
    'Контакты': ['адрес', 'сеть', 'вайфай', 'телефон', 'номер', 'звонок', 'сайт', 'трубка', 'звонок', 'почта', 'связь', 'письмо', 'ответ', 'оповещение', 'повестка'],
    'Расположение': ['доступ', 'расположение', 'территория', 'метро', 'парк', 'парковка', 'стоянка', 'езда', 'пандус', 'шлагбаум', 'ворота'],
    'Судья': ['судья', 'судей'],
    'Сотрудники': ['обращение', 'девочка', 'женщина', 'девушка', 'специалист', 'работник', 'сторож', 'вахта', 'прокурор', 'коллектив', 'исполнитель', 'секретарь', 'помощник', 'персонал', 'охранник', 'пристав', 'канцелярия', 'сотрудник', 'начальник'],
    'Функционирование суда': ['турникет', 'пропуск', 'вайфай', 'процесс', 'интернет', 'задержка', 'ожидание', 'очередь', 'отношение', 'логистика', 'обслуживание', 'коррупция', 'работа', 'прием', 'судебный', 'аппарат', 'дело', 'документ', 'правосудие'],
    'Суд': ['участок', 'организация', 'атмосфера', 'обстановка', 'заведение', 'филиал', 'суд', 'здание', 'контора', 'учреждение'],
    'Строение': ['санузел', 'внутри', 'ремонт', 'туалет', 'гардероб', 'вестибюль', 'архитектура', 'сооружение', 'коридор', 'лифт', 'прихожая', 'место', 'зал', 'помещение', 'комната', 'кабинет', 'приемная'],
    'Заседание': ['заседание', 'рассмотрение', 'решение', 'приговор', 'слушание'],
    'Буфет': ['столовая', 'еда', 'кафе', 'буфет', 'блюдо'],
    'Другое': []
}

def check_theme(aspect):
    """Проверка темы для нормализованного аспекта"""
    for theme in themes:
        for keyword in themes[theme]:
            if keyword in aspect or aspect in keyword:
                return theme
    return 'Другое'

# Удаляем дубликаты после нормализации
unique_aspects = sorted(list(set(normalized_aspects)))
print(f"Всего уникальных аспектов после нормализации: {len(unique_aspects)}")

# Категоризация аспектов
with open("categories_aspects.json", "w", encoding="utf-8") as file:
    result = {}
    for key in themes.keys():
        result[key] = []
    
    for aspect in unique_aspects:
        theme = check_theme(aspect)
        result[theme].append(aspect)
    
    json.dump(result, file, ensure_ascii=False, indent=2)

print("Готово! Результат сохранен в categories_aspects.json")

# Дополнительно: сохранение словаря соответствий исходных и нормализованных форм
mapping = {}
for original, normalized in zip(aspects, normalized_aspects):
    if original not in mapping:
        mapping[original] = normalized

with open("normalization_mapping.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)
