import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ваш существующий код загрузки и обработки данных
aspects = []
court_reviews = {}
google_reviews = {}
with open('all_court_reviews.json', 'r') as file:
    data = json.load(file)
    court_reviews = data.copy()
with open('filtered_google_reviews.json', 'r') as file:
    data = json.load(file)
    google_reviews = data.copy()
with open('allaspects.json', 'r') as file:
    d = json.load(file)
    for court in d:
        for asp in range(len(d[court])):
            for word in d[court][asp]:
                aspects += [[word.lower(), d[court][asp][word].lower(), court_reviews[court]['reviews'][asp]['date'].split("T")[0]]]
with open('all_google_aspects.json', 'r') as file:
    d = json.load(file)
    for court in d:
        for asp in range(0, len(d[court])):
            for word in d[court][asp]:
                aspects += [[word.lower(), d[court][asp][word].lower(), google_reviews[court]['reviews'][asp]['date'].split("T")[0]]]

months = ['январ', 'феврал', 'март', 'апрел', 'ма', 'июн', 'июл', 'август', 'сентябр', 'октябр', 'ноябр', 'декабр']
for i in range(len(aspects)):
    for m in range(len(months)):
        if months[m] in aspects[i][2]:
            parts = aspects[i][2].split(" ")
            if len(parts) < 3:
                parts += ['2025']
            aspects[i][2] = f"{parts[2]}-{(m+1)//10}{(m+1)%10}-{parts[0]}"

themes = {
    'Контакты': ['телеф', 'номер', 'звон', 'сайт', 'трубк', 'званк', 'почт'],
    'Расположение': ['располож', 'территория', 'метро', 'парк', 'порков', 'стоянк', 'езд', 'пандус', 'шлагба', 'ворот'],
    'Судья': ['судь', 'судей'],
    'Сотрудники': ['девочк', 'женщин', 'девушк', 'специал', 'работн', 'сторож', 'вахт', 'прокурор', 'коллектив', 'исполн', 'сикрет', 'секретар', 'помощни', 'работн', 'персонал', 'охран', 'пристав', 'канцел', 'сотр', 'начал'],
    'Функционирование суда': ['процесс', 'интерн', 'задерж', 'ожидан', 'очеред', 'отношен', 'логист', 'обслуж', 'корруп', 'работ', 'прием', 'приём', 'судебн', 'аппар', 'дел', 'докумен', 'правосу'],
    'Суд': ['участк', 'организация', 'атмосфера', 'обстанов', 'участок', 'заведение', 'филиал', 'суд', 'здан', 'контор', 'кантор', 'учрежд'],
    'Строение': ['внутри', 'ремонт', 'туалет', 'гардероб', 'вестиб', 'архитект', 'сооруж', 'коридор', 'лифт', 'прихож', 'мест', 'зал', 'помещ', 'комнат', 'кабинет', 'приёмн', 'приемн'],
    'Заседание': ['засед', 'рассмотр', 'решен', 'приговор'],
    'Буфет': ['столов', 'еда', 'каф', 'буфет']
}

def check_theme(aspect):
    for theme in themes:
        for i in themes[theme]:
            if i in aspect:
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
    title='Тренды количества аспектов по категориям (скользящее среднее за 30 дней)',
    xaxis_title='Дата',
    yaxis_title='Количество аспектов',
    hovermode='x unified',
    height=600
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

# Создаем фигуру с двумя подграфиками: круговая диаграмма и столбчатая
main_fig = make_subplots(
    rows=2,
    cols=1,
    specs=[[{'type': 'domain'}], [{'type': 'bar'}]],
    subplot_titles=('Распределение аспектов по категориям', 'Соотношение тональностей для каждой категории')
)

# Круговая диаграмма
main_fig.add_trace(
    go.Pie(
        labels=categories,
        values=total_reviews_per_category,
        hole=0.4,
        hoverinfo='label+percent',
        textinfo='label+percent'
    ),
    row=1,
    col=1
)

# Столбчатая диаграмма с нейтральными отзывами
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

# Обновляем макет для интерактивности и оформления
main_fig.update_layout(
    height=800,
    title_text='Дашборд отзывов',
    barmode='stack'
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
        }}
    </style>
</head>
<body>
    <h1>Анализ отзывов о судах</h1>
    <div class="graph-container">
        {main_graph}
    </div>
    <div class="graph-container">
        {trend_graph}
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

