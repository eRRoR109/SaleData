import pandas as pd
import plotly.express as px


def generate_plot(selected_date_range='all', selected_vendor='all', selected_model='all', selected_dealer='all'):
    """
    Функция генерирования графика
    :param selected_date_range: возможные данные: ['all', '1m', '3m', '6m', '1y', 'start_data end_data']
    :param selected_vendor:
    :param selected_model:
    :param selected_dealer:
    :return:
    """
    sale_data = pd.read_csv('sale_data.csv')
    sale_data["date"] = pd.to_datetime(sale_data["date"])

    # Фильтрация по датам
    if selected_date_range == 'all':
        pass
    elif selected_date_range == '1m':
        sale_data = sale_data[sale_data["date"] >= sale_data["date"][sale_data.index[-1]] - pd.DateOffset(months=1)]
    elif selected_date_range == '3m':
        sale_data = sale_data[sale_data["date"] >= sale_data["date"][sale_data.index[-1]] - pd.DateOffset(months=3)]
    elif selected_date_range == '6m':
        sale_data = sale_data[sale_data["date"] >= sale_data["date"][sale_data.index[-1]] - pd.DateOffset(months=6)]
    elif selected_date_range == '1y':
        sale_data = sale_data[sale_data["date"] >= sale_data["date"][sale_data.index[-1]] - pd.DateOffset(years=1)]
    else:
        ...

    # Фильтрация по выбранной марке
    if selected_vendor == 'all':
        pass
    else:
        sale_data = sale_data[sale_data['vendor'] == selected_vendor]

    # Фильтрация по модели
    if selected_model == 'all':
        pass
    else:
        sale_data = sale_data[sale_data['model'] == selected_model]

    # Фильтрация по дилеру
    if selected_dealer == 'all':
        pass
    else:
        sale_data = sale_data[sale_data['dealer'] == selected_dealer]

    # Группировка данных и семплирование
    sale_data = sale_data.groupby('date')['contract'].sum()
    sale_data.index = pd.to_datetime(sale_data.index)

    if selected_date_range == '1y' or 'all':
        sale_data = sale_data.resample('M').sum()

    try:
        start_contracts = sale_data.iloc[0]
        end_contracts = sale_data.iloc[-1]
        percentage_change = f'{((end_contracts - start_contracts) / start_contracts) * 100}%'
    except ZeroDivisionError:
        percentage_change = f'+{sale_data.iloc[-1]}пт'

    # Создание графика
    fig = px.line(x=sale_data.index, y=sale_data.values)
    fig_json = fig.to_json()

    return fig_json, round(sale_data.mean()), percentage_change



