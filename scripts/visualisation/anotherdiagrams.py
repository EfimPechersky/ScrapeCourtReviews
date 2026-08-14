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

# Функция для создания гистограммы по категориям для указанной тональности
def create_sentiment_histogram(sentiment_type, sentiment_name, color):
    """
    Создает гистограмму для указанной тональности
    
    Parameters:
    sentiment_type: 'positive', 'negative' или 'neutral'
    sentiment_name: название для отображения ('Положительных', 'Отрицательных', 'Нейтральные')
    color: цвет столбцов
    """
    # Подсчет аспектов по категориям для указанной тональности
    category_counts = {}
    
    for theme in themes:
        if theme == 'Другое':
            continue
        theme_df = df[df['theme'] == theme]
        if len(theme_df) > 0:
            category_counts[theme] = len(theme_df[theme_df['sentiment'] == sentiment_type])
        else:
            category_counts[theme] = 0
    
    # Сортировка категорий по убыванию (только те, где есть аспекты данной тональности)
    sorted_categories = sorted([(theme, count) for theme, count in category_counts.items() if count > 0], 
                              key=lambda x: x[1], reverse=True)
    
    if not sorted_categories:
        print(f"⚠️ Нет {sentiment_name.lower()} аспектов для отображения")
        return None
    
    categories = [cat[0] for cat in sorted_categories]
    counts = [cat[1] for cat in sorted_categories]
    
    # Расчет процентов от общего числа аспектов в категории
    percentages = []
    totals_in_category = []
    for i, cat in enumerate(sorted_categories):
        theme = cat[0]
        total_in_category = len(df[df['theme'] == theme])
        totals_in_category.append(total_in_category)
        if total_in_category > 0:
            percentages.append((cat[1] / total_in_category) * 100)
        else:
            percentages.append(0)
    
    # Создание гистограммы
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=counts,
        name=sentiment_name,
        marker_color=color,
        text=[f'{count}<br>({pct:.1f}%)' for count, pct in zip(counts, percentages)],
        textposition='outside',
        textfont=dict(size=40, color='black'),
        width=0.9,
        customdata=list(zip(percentages, totals_in_category)),
        hovertemplate='<b>%{x}</b><br>' +
                      f'{sentiment_name}: %{{y}}<br>' +
                      '%{customdata[0]:.1f}% от категории<br>' +
                      'Всего в категории: %{customdata[1]}<extra></extra>'
    ))
    
    # Добавляем общее количество аспектов в категории над столбцами
    annotations = []
    for i, cat in enumerate(sorted_categories):
        theme = cat[0]
        total_in_category = len(df[df['theme'] == theme])
        
    
    fig.update_layout(
        title=dict(
            text=f'Распределение {sentiment_name.lower()[:-1]}x аспектов по категориям',
            font=dict(size=30, color='black'),
            x=0.5
        ),
        xaxis_title='Категория',
        yaxis_title=f'Количество {sentiment_name.lower()} аспектов',
        height=600,
        showlegend=True,
        bargap=0.3,
        bargroupgap=0.1,
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.98,
            font=dict(size=14)
        ),
        margin=dict(t=100, b=100, l=40, r=40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        annotations=annotations
    )
    
    # Настройка осей
    fig.update_xaxes(
        tickfont=dict(size=16),
        tickangle=-45,
        gridcolor='lightgray',
        showgrid=True,
        title_font=dict(size=14)
    )
    fig.update_yaxes(
        tickfont=dict(size=16),
        gridcolor='lightgray',
        showgrid=True,
        title_font=dict(size=14)
    )
    
    # Увеличиваем диапазон оси Y для аннотаций
    if counts:
        max_y = max(counts)
        fig.update_yaxes(range=[0, max_y * 1.25])
    
    return fig

# Создаем гистограммы
fig_positive = create_sentiment_histogram('positive', 'Положительные', 'green')
fig_negative = create_sentiment_histogram('negative', 'Отрицательные', 'red')

# Объединение гистограмм в один HTML файл
if fig_positive and fig_negative:
    combined_html = """
    <html>
    <head>
        <title>Анализ положительных и отрицательных аспектов отзывов о судах</title>
        <style>
            .graph-container {{
                width: 90%;
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
                margin-bottom: 30px;
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
                font-size: 14px;
                margin-top: 20px;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 5px;
                border-left: 4px solid #4CAF50;
            }}
            .separator {{
                text-align: center;
                margin: 20px 0;
                font-size: 18px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <h1>📊 Анализ тональностей аспектов отзывов о судах</h1>
        <div class="graph-container">
            {graph_positive}
        </div>
        <div class="separator">✦ ✦ ✦</div>
        <div class="graph-container">
            {graph_negative}
        </div>
        <div class="note">
            📌 <b>Пояснение:</b><br>
            • Над каждым столбцом указано общее количество аспектов в категории<br>
            • На столбцах указано количество аспектов и их процент от общего числа аспектов в категории<br>
            • Наведите курсор на столбец для получения детальной информации
        </div>
    </body>
    </html>
    """.format(
        graph_positive=fig_positive.to_html(full_html=False, include_plotlyjs='cdn'),
        graph_negative=fig_negative.to_html(full_html=False, include_plotlyjs='cdn')
    )
    
    # Сохраняем в файл
    with open('positive_negative_histograms.html', 'w', encoding='utf-8') as f:
        f.write(combined_html)
    
    print("✅ Гистограммы успешно созданы и сохранены в файл 'positive_negative_histograms.html'")
    print("📊 Первая гистограмма: только ПОЛОЖИТЕЛЬНЫЕ аспекты по категориям")
    print("📈 Вторая гистограмма: только ОТРИЦАТЕЛЬНЫЕ аспекты по категориям")
    print("📌 Каждый столбец показывает количество аспектов и их процент от общей категории")
    
else:
    print("❌ Не удалось создать одну или обе гистограммы из-за отсутствия данных")
    if not fig_positive:
        print("   - Нет положительных аспектов для отображения")
    if not fig_negative:
        print("   - Нет отрицательных аспектов для отображения")
