import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Загрузка данных
aspects = []
court_reviews = {}
google_reviews = {}

with open('yandex_reviews.json', 'r') as file:
    data = json.load(file)
    court_reviews = data.copy()
with open('google_reviews.json', 'r') as file:
    data = json.load(file)
    google_reviews = data.copy()
with open('yandex_aspects.json', 'r') as file:
    d = json.load(file)
    for court in d:
        for asp in range(len(d[court])):
            for word in d[court][asp]:
                aspects += [[word.lower(), d[court][asp][word].lower(), court_reviews[court][asp]['date'].split("T")[0]]]
with open('google_aspects.json', 'r') as file:
    d = json.load(file)
    for court in d:
        for asp in range(0, len(d[court])):
            for word in d[court][asp]:
                aspects += [[word.lower(), d[court][asp][word].lower(), google_reviews[court][asp]['date'].split("T")[0]]]

# Обработка дат
months = ['январ', 'феврал', 'март', 'апрел', 'ма', 'июн', 'июл', 'август', 'сентябр', 'октябр', 'ноябр', 'декабр']
for i in range(len(aspects)):
    for m in range(len(months)):
        if months[m] in aspects[i][2]:
            parts = aspects[i][2].split(" ")
            if len(parts) < 3:
                parts += ['2025']
            aspects[i][2] = f"{parts[2]}-{(m+1)//10}{(m+1)%10}-{parts[0]}"

# Категории аспектов
with open("new_categories_aspects.json", 'r', encoding="UTF-8") as file:
    themes=json.load(file)
    
def check_theme(aspect):
    for theme in themes:
        if aspect in themes[theme]:
            return theme
    return 'Другое'

# Создаем DataFrame
df = pd.DataFrame(aspects, columns=['aspect', 'sentiment', 'date'])
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df['theme'] = df['aspect'].apply(check_theme)

# Подсчет аспектов по тональностям для общей гистограммы
sentiment_counts = {
    'positive': len(df[df['sentiment'] == 'positive']),
    'negative': len(df[df['sentiment'] == 'negative']),
    'neutral': len(df[df['sentiment'] == 'neutral'])
}

total_aspects = sum(sentiment_counts.values())
sentiment_percentages = {
    'positive': (sentiment_counts['positive'] / total_aspects * 100),
    'negative': (sentiment_counts['negative'] / total_aspects * 100),
    'neutral': (sentiment_counts['neutral'] / total_aspects * 100)
}

# Функция для определения позиции текста
def get_text_position(value, max_value, percentage):
    if percentage < 15 or value < max_value * 0.1:
        return 'outside'
    else:
        return 'inside'

# Находим максимальное значение для первой гистограммы
max_value_first = max(sentiment_counts.values())

# Создание общей гистограммы (возвращаем исходный вид)
fig1 = go.Figure()

# Для каждого столбца определяем позицию текста
positions1 = []
for sentiment in ['positive', 'negative', 'neutral']:
    value = sentiment_counts[sentiment]
    percentage = sentiment_percentages[sentiment]
    positions1.append(get_text_position(value, max_value_first, percentage))

fig1.add_trace(go.Bar(
    x=['Позитивные', 'Негативные', 'Нейтральные'],
    y=[sentiment_counts['positive'], sentiment_counts['negative'], sentiment_counts['neutral']],
    text=[f'{sentiment_percentages["positive"]:.1f}%', 
          f'{sentiment_percentages["negative"]:.1f}%', 
          f'{sentiment_percentages["neutral"]:.1f}%'],
    textposition=positions1,
    textfont=dict(size=16, color='black'),
    marker_color=['green', 'red', 'gray'],
    name='Аспекты',
    width=0.5,
    textangle=0,
    insidetextanchor='middle',
    outsidetextfont=dict(size=16, color='black')
))

fig1.update_layout(
    title=dict(text='Общее распределение аспектов по тональности', font=dict(size=20)),
    xaxis_title='Тональность',
    yaxis_title='Количество аспектов',
    height=550,
    showlegend=False,
    bargap=0.5,
    uniformtext=dict(mode='show', minsize=16),
    margin=dict(t=80, b=50, l=60, r=60),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig1.update_xaxes(tickfont=dict(size=14), gridcolor='lightgray', showgrid=True)
fig1.update_yaxes(tickfont=dict(size=12), gridcolor='lightgray', showgrid=True, 
                  range=[0, max_value_first * 1.15])

# Подсчет аспектов по категориям (исключая "Другое")
category_sentiments = {}
print(themes)
for theme in themes:
    #if theme == 'Другое':
    #    continue
    theme_df = df[df['theme'] == theme]
    if len(theme_df) > 0:
        category_sentiments[theme] = {
            'positive': len(theme_df[theme_df['sentiment'] == 'positive']),
            'negative': len(theme_df[theme_df['sentiment'] == 'negative']),
            'neutral': len(theme_df[theme_df['sentiment'] == 'neutral']),
            'total': len(theme_df)
        }

# Сортировка категорий по общему количеству аспектов (от большего к меньшему)
sorted_categories = sorted(category_sentiments.items(), key=lambda x: x[1]['total'], reverse=True)

# Подготовка данных для гистограммы по категориям
categories = [cat[0] for cat in sorted_categories]
positive_counts = [cat[1]['positive'] for cat in sorted_categories]
negative_counts = [cat[1]['negative'] for cat in sorted_categories]
neutral_counts = [cat[1]['neutral'] for cat in sorted_categories]

# Расчет процентов для каждой категории
positive_percentages = []
negative_percentages = []
neutral_percentages = []

for i, cat in enumerate(sorted_categories):
    total = cat[1]['total']
    if total > 0:
        positive_percentages.append(cat[1]['positive'] / total * 100)
        negative_percentages.append(cat[1]['negative'] / total * 100)
        neutral_percentages.append(cat[1]['neutral'] / total * 100)
    else:
        positive_percentages.append(0)
        negative_percentages.append(0)
        neutral_percentages.append(0)

# Создание stacked bar chart с подписями над столбцами
fig2 = go.Figure()

# Добавляем позитивные сегменты
fig2.add_trace(go.Bar(
    x=categories,
    y=positive_counts,
    name='Позитивные',
    marker_color='green',
    text='',
    width=0.7,
    hovertemplate='<b>%{x}</b><br>' +
                  'Позитивные: %{y} (%{customdata:.1f}%)<extra></extra>',
    customdata=positive_percentages
))

# Добавляем нейтральные сегменты
fig2.add_trace(go.Bar(
    x=categories,
    y=neutral_counts,
    name='Нейтральные',
    marker_color='gray',
    text='',
    width=0.7,
    hovertemplate='<b>%{x}</b><br>' +
                  'Нейтральные: %{y} (%{customdata:.1f}%)<extra></extra>',
    customdata=neutral_percentages
))

# Добавляем негативные сегменты
fig2.add_trace(go.Bar(
    x=categories,
    y=negative_counts,
    name='Негативные',
    marker_color='red',
    text='',
    width=0.7,
    hovertemplate='<b>%{x}</b><br>' +
                  'Негативные: %{y} (%{customdata:.1f}%)<extra></extra>',
    customdata=negative_percentages
))

# Создаем подписи над столбцами
annotations = []
for i, cat in enumerate(categories):
    total = category_sentiments[cat]['total']
    pos_pct = positive_percentages[i]
    neg_pct = negative_percentages[i]
    neu_pct = neutral_percentages[i]
    
    # Формируем текст подписи
    annotation_text = (
        f'<b>Всего: {total}</b><br>' +
        f'<span style="color:green">▲ {pos_pct:.1f}%</span><br>' +
        f'<span style="color:gray">● {neu_pct:.1f}%</span><br>' +
        f'<span style="color:red">▼ {neg_pct:.1f}%</span>'
    )
    
    # Вычисляем y-координату для подписи (над самым высоким столбцом)
    max_height = positive_counts[i] + neutral_counts[i] + negative_counts[i]
    
    annotations.append(dict(
        x=cat,
        y=max_height,
        text=annotation_text,
        showarrow=False,
        font=dict(size=12),
        xanchor='center',
        yanchor='bottom',
        bgcolor='rgba(255, 255, 255, 0.95)',
        bordercolor='lightgray',
        borderwidth=1,
        borderpad=4
    ))

fig2.update_layout(
    title=dict(text='Распределение тональностей по категориям', font=dict(size=40)),
    xaxis_title=dict(text='Категория', font=dict(size=20)),
    yaxis_title=dict(text='Количество аспектов', font=dict(size=20)),
    barmode='stack',
    height=800,
    bargap=0.25,
    legend=dict(
        yanchor="top",
        y=0.98,
        xanchor="right",
        x=0.98,
        font=dict(size=14),
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='black',
        borderwidth=1
    ),
    margin=dict(t=120, b=100, l=60, r=60),
    plot_bgcolor='white',
    paper_bgcolor='white',
    annotations=annotations
)

# Настройка осей
fig2.update_xaxes(tickfont=dict(size=20), tickangle=-45, gridcolor='lightgray', showgrid=True)
fig2.update_yaxes(tickfont=dict(size=12), gridcolor='lightgray', showgrid=True)

# Увеличиваем диапазон оси Y для аннотаций
max_y = max([sum([positive_counts[i], neutral_counts[i], negative_counts[i]]) for i in range(len(categories))])
fig2.update_yaxes(range=[0, max_y * 1.35])

# Объединение обеих гистограмм в один HTML файл
combined_html = """
<html>
<head>
    <title>Анализ тональностей аспектов отзывов</title>
    <style>
        .graph-container {{
            width: 90%%;
            margin: 0 auto 50px auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            font-family: Arial, sans-serif;
            color: #333;
        }}
        body {{
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }}
        .note {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <h1>Анализ тональностей аспектов отзывов о судах</h1>
    <div class="graph-container">
        {graph1}
    </div>
    <div class="graph-container">
        {graph2}
    </div>
    <div class="note">
        📊 <b>Информация о втором графике:</b><br>
        • Над каждым столбцом указано общее количество аспектов и процентное соотношение по тональностям<br>
        • <span style="color:green">▲</span> Позитивные &nbsp;&nbsp; <span style="color:gray">●</span> Нейтральные &nbsp;&nbsp; <span style="color:red">▼</span> Негативные<br>
        • Наведите курсор на сегменты столбцов, чтобы увидеть точные значения
    </div>
</body>
</html>
""".format(
    graph1=fig1.to_html(full_html=False, include_plotlyjs='cdn'),
    graph2=fig2.to_html(full_html=False, include_plotlyjs='cdn')
)

# Сохраняем в файл
with open('histograms_reviews.html', 'w', encoding='utf-8') as f:
    f.write(combined_html)

print("✅ Гистограммы успешно созданы и сохранены в файл 'histograms_reviews.html'")
print("📊 Первая гистограмма: процентные подписи внутри/снаружи столбцов")
print("📈 Вторая гистограмма: информационные блоки над столбцами (никаких перекрытий!)")
