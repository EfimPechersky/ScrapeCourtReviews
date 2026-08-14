import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ваш существующий код загрузки и обработки данных
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

months = ['январ', 'феврал', 'март', 'апрел', 'ма', 'июн', 'июл', 'август', 'сентябр', 'октябр', 'ноябр', 'декабр']
for i in range(len(aspects)):
    for m in range(len(months)):
        if months[m] in aspects[i][2]:
            parts = aspects[i][2].split(" ")
            if len(parts) < 3:
                parts += ['2025']
            aspects[i][2] = f"{parts[2]}-{(m+1)//10}{(m+1)%10}-{parts[0]}"

with open("new_categories_aspects.json", 'r', encoding="UTF-8") as file:
    themes=json.load(file)
    
def check_theme(aspect):
    for theme in themes:
        if aspect in themes[theme]:
            return theme
    return 'Другое'

# Создаем DataFrame для анализа временных трендов
df = pd.DataFrame(aspects, columns=['aspect', 'sentiment', 'date'])
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df['theme'] = df['aspect'].apply(check_theme)

# Группируем по дате и категории для временных трендов
df_trend = df.groupby(['date', 'theme']).size().unstack(fill_value=0).reset_index()

# Вычисляем скользящее среднее за 30 дней для каждой категории
for theme in df_trend.columns[1:]:
    df_trend[f'{theme}_ma30'] = round(df_trend[theme].rolling(window=30, min_periods=1).mean(),2)

# Создаем график трендов
trend_fig = go.Figure()

for theme in df_trend.columns[1:]:
    if '_ma30' in theme:
        original_theme = theme.replace('_ma30', '')
        trend_fig.add_trace(go.Scatter(
            x=df_trend['date'],
            y=df_trend[theme],
            mode='lines',
            name=f'{original_theme}',
            line=dict(width=2)
        ))

trend_fig.update_layout(
    title=dict(text='Тренды количества аспектов по категориям (скользящее среднее за 30 дней)', font=dict(size=20)),
    xaxis_title='Дата',
    yaxis_title='Количество аспектов',
    hovermode='x unified',
    height=600,
    legend=dict(
        font=dict(size=16)
    )
)
trend_fig.update_xaxes(
    title_font=dict(size=16),  # ← Размер шрифта заголовка оси X
    tickfont=dict(size=14)     # ← Размер шрифта меток оси X
)

trend_fig.update_yaxes(
    title_font=dict(size=16),  # ← Размер шрифта заголовка оси Y
    tickfont=dict(size=14)     # ← Размер шрифта меток оси Y
)

# Ваш существующий код для создания первых графиков
count_themes = {
    'Контакты': {},
    'Расположение': {},
    'Судья': {},
    'Сотрудники': {},
    'Функционирование суда': {},
    'Суд': {},
    'Строение': {},
    'Заседание': {},
    'Исход дела':{},
    'Буфет': {},
    'Другое': {}
}

for i in count_themes:
    count_themes[i]['positive'] = 0
    count_themes[i]['negative'] = 0
    count_themes[i]['neutral'] = 0

for i in aspects:
    thm = check_theme(i[0])
    count_themes[thm][i[1]] += 1

# Расчет общего количества отзывов по категориям
total_reviews_per_category = [r['positive'] + r['negative'] + r['neutral'] for t, r in count_themes.items()]
categories = [i for i in count_themes]
positive_counts = [r['positive'] for t, r in count_themes.items()]
negative_counts = [r['negative'] for t, r in count_themes.items()]
neutral_counts = [r['neutral'] for t, r in count_themes.items()]

# 🔧 ИСПРАВЛЕННАЯ КРУГОВАЯ ДИАГРАММА С ОТСТУПАМИ
# Создаем фигуру с увеличенным размером для круговой диаграммы
main_fig = make_subplots(
    rows=2,
    cols=1,
    specs=[[{'type': 'domain'}], [{'type': 'bar'}]],
    subplot_titles=('', ''),
    vertical_spacing=0.2  # Увеличиваем расстояние между графиками
)

# Круговая диаграмма с настройками для лучшего отображения всех категорий
main_fig.add_trace(
    go.Pie(
        labels=categories,
        values=total_reviews_per_category,
        hole=0.35,
        hoverinfo='label+percent+value',
        textinfo='label+percent',
        textposition='outside',  # Текст снаружи круговой диаграммы
        textfont=dict(size=11),
        marker=dict(
            line=dict(color='white', width=2)
        ),
        sort=False,
        direction='clockwise',
        rotation=90,
        insidetextorientation='horizontal'
    ),
    row=1,
    col=1
)

# Столбчатая диаграмма
main_fig.add_trace(
    go.Bar(
        x=categories,
        y=positive_counts,
        name='Позитивные',
        marker_color='green'
    ),
    row=2,
    col=1
)
main_fig.add_trace(
    go.Bar(
        x=categories,
        y=neutral_counts,
        name='Нейтральные',
        marker_color='gray'
    ),
    row=2,
    col=1
)
main_fig.add_trace(
    go.Bar(
        x=categories,
        y=negative_counts,
        name='Негативные',
        marker_color='red'
    ),
    row=2,
    col=1
)

# Обновляем макет с увеличенными отступами
main_fig.update_layout(
    height=1100,  # Еще увеличиваем высоту
    title_text='Дашборд отзывов',
    title_font_size=16,
    barmode='stack',
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.2,  # Поднимаем легенду выше
        xanchor="center",
        x=0.5,
        font=dict(size=12)
    ),
    margin=dict(
        t=100,   # Верхний отступ для заголовка
        b=80,    # Нижний отступ
        l=80,    # Левый отступ
        r=80,    # Правый отступ
        pad=10
    )
)

# Дополнительные настройки для круговой диаграммы
main_fig.update_traces(
    textposition='outside',
    textinfo='label+percent',
    hoverinfo='label+percent+value',
    insidetextorientation='radial',
    textfont=dict(size=10, color='black'),
    marker=dict(line=dict(color='white', width=2)),
    row=1, col=1
)

# Создаем общий HTML файл с обоими графиками
from plotly.io import write_html

# Создаем div для обоих графиков
combined_html = """
<html>
<head>
    <title>Дашборд отзывов</title>
    <style>
        .graph-container {{
            width: 100%;
            margin-bottom: 50px;
        }}
        h1 {{
            text-align: center;
            font-family: Arial, sans-serif;
            margin-bottom: 30px;
        }}
        .note {{
            text-align: center;
            font-family: Arial, sans-serif;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }}
        /* Увеличиваем область отображения для круговой диаграммы */
        .js-plotly-plot .plotly .main-svg {{
            overflow: visible !important;
        }}
    </style>
</head>
<body>
    <h1>📊 Анализ отзывов о судах</h1>
    <div class="graph-container">
        {main_graph}
    </div>
    <div class="graph-container">
        {trend_graph}
    </div>
    <div class="note">
        💡 Подсказка: Наведите курсор на сектор круговой диаграммы для просмотра точных значений.<br>
        🔍 Используйте колесико мыши для масштабирования, если подписи кажутся слишком маленькими.
    </div>
</body>
</html>
""".format(
    main_graph=main_fig.to_html(full_html=False),
    trend_graph=trend_fig.to_html(full_html=False)
)

# Сохраняем в файл
with open('dashboard_reviews.html', 'w', encoding='utf-8') as f:
    f.write(combined_html)

print("✅ Дашборд успешно создан! Откройте файл 'dashboard_reviews.html'")
print("\n📐 Что изменено для устранения перекрытий:")
print("• Текст круговой диаграммы вынесен СНАРУЖИ (textposition='outside')")
print("• Увеличены отступы: верхний 100px, нижний 80px, левый/правый 80px")
print("• Легенда поднята выше (y=1.08) и отцентрирована")
print("• Увеличено расстояние между графиками (vertical_spacing=0.2)")
print("• Общая высота дашборда увеличена до 1100px")
