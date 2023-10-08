import pandas as pd
from pandas.tseries.offsets import DateOffset

sales = pd.read_csv('./sale_data.csv', index_col=0)
sales['date'] = pd.to_datetime(sales['date'])


# -------------------Мгновенный скользящий--------------------------
def instant_moving_index(
        sale_type: str,  # Контракт/Расторжение
        input_date: str,  # Дата, для которой мы считаем индекс
        dealer: str = None,  # id дилера
        vendor: str = None,  # Марка машины
        model: str = None  # Модель
) -> float:
    result_df = sales  # result_df - вспомогательный ДФ, который мы будем получать, фильтруя исходный по параметрам, и по которому будем считать индекс
    date = pd.to_datetime(input_date)  # перевожу в формат даты

    if dealer is not None:
        mask_dealer = result_df['dealer'] == dealer  # здесь просто фильтрация по параметрам с помощью масок
        result_df = result_df[mask_dealer]

    if vendor is not None:
        mask_vendor = result_df['vendor'] == vendor
        result_df = result_df[mask_vendor]

    if model is not None:
        mask_model = result_df['model'] == model
        result_df = result_df[mask_model]

    mask_sale_type = result_df['sale_type'] == sale_type
    result_df = result_df[mask_sale_type]

    mask_date = (date - pd.offsets.Day(6) <= result_df['date']) & (result_df['date'] < date)
    result_df = result_df[mask_date].sort_values('date')

    denominator = result_df[result_df['date'] < date - pd.offsets.Day(3)].shape[0]  # определяю знаменатель индекса

    numerator = result_df[result_df['date'] >= date - pd.offsets.Day(3)].shape[0]  # и числитель

    if denominator == 0:  # здесь всякие предостережения на случай, если знаменатель = 0
        if numerator == 0:
            index = 1
        else:
            index = numerator
    else:
        index = numerator / denominator

    return index


def instant_moving_index_interval(
        sale_type: str,
        start_date: str,  # начало временного интервала
        end_date: str,  # конец временного интервала
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    instant_moving_index_array = pd.DataFrame(
        # Определяю датафрейм, к нему буду присоединять с конца индексы по ходу цикла
        {
            'date': [],
            'index': []
        }
    )
    instant_moving_index_array['date'] = pd.to_datetime(instant_moving_index_array['date'])  # перевожу формат на дату

    start_date = pd.to_datetime(start_date)  # здесь тоже
    end_date = pd.to_datetime(end_date)

    for step_date in pd.date_range(start=start_date, end=end_date):  # и собственно цикл с шаком в 1 день
        step_index = instant_moving_index(sale_type, step_date, dealer, vendor, model)  # расчёт индекса
        instant_moving_index_array.loc[len(instant_moving_index_array.index)] = [step_date,
                                                                                 step_index]  # добавляю его в ДФ

    return instant_moving_index_array


# ---------------------------Мгновенный год-год--------------------------
def instant_year_year_index(
        sale_type: str,
        input_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None) -> float:
    result_df = sales
    date = pd.to_datetime(input_date)

    if dealer is not None:
        mask_dealer = result_df['dealer'] == dealer
        result_df = result_df[mask_dealer]

    if vendor is not None:
        mask_vendor = result_df['vendor'] == vendor
        result_df = result_df[mask_vendor]

    if model is not None:
        mask_model = result_df['model'] == model
        result_df = result_df[mask_model]

    mask_sale_type = result_df['sale_type'] == sale_type
    result_df = result_df[mask_sale_type]

    mask_date_current_year = (date - DateOffset(days=3) <= result_df['date']) & (result_df['date'] < date)
    result_df_current_year = result_df[mask_date_current_year].sort_values('date')

    mask_date_last_year = (date - DateOffset(years=1, days=3) <= result_df['date']) & (
            result_df['date'] < date - DateOffset(years=1))
    result_df_last_year = result_df[mask_date_last_year].sort_values('date')

    denominator = result_df_last_year.shape[0]

    numerator = result_df_current_year.shape[0]

    if denominator == 0:
        if numerator == 0:
            index = 1
        else:
            index = numerator
    else:
        index = numerator / denominator

    return index


def instant_year_year_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    instant_year_year_index_df = pd.DataFrame(
        {
            'date': [],
            'index': []
        }
    )
    instant_year_year_index_df['date'] = pd.to_datetime(instant_year_year_index_df['date'])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    for step_date in pd.date_range(start=start_date, end=end_date):
        step_index = instant_year_year_index(sale_type, step_date, dealer, vendor, model)
        instant_year_year_index_df.loc[len(instant_year_year_index_df.index)] = [step_date, step_index]

    return instant_year_year_index_df


# -----------Текущий скользящий------------------------------
def current_moving_index(
        sale_type: str,
        input_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None) -> float:
    result_df = sales
    date = pd.to_datetime(input_date)

    if dealer is not None:
        mask_dealer = result_df['dealer'] == dealer
        result_df = result_df[mask_dealer]

    if vendor is not None:
        mask_vendor = result_df['vendor'] == vendor
        result_df = result_df[mask_vendor]

    if model is not None:
        mask_model = result_df['model'] == model
        result_df = result_df[mask_model]

    mask_sale_type = result_df['sale_type'] == sale_type
    result_df = result_df[mask_sale_type]

    mask_date_current_month = (date - DateOffset(months=1) <= result_df['date']) & (result_df['date'] < date)
    result_df_current_month = result_df[mask_date_current_month].sort_values('date')

    mask_date_last_month = (date - DateOffset(months=2) <= result_df['date']) & (
            result_df['date'] < date - DateOffset(months=1))
    result_df_last_month = result_df[mask_date_last_month].sort_values('date')

    denominator = result_df_last_month.shape[0]

    numerator = result_df_current_month.shape[0]

    if denominator == 0:
        if numerator == 0:
            index = 1
        else:
            index = numerator
    else:
        index = numerator / denominator

    return index


def current_moving_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    current_moving_index_df = pd.DataFrame(
        {
            'date': [],
            'index': []
        }
    )
    current_moving_index_df['date'] = pd.to_datetime(current_moving_index_df['date'])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    for step_date in pd.date_range(start=start_date, end=end_date):
        step_index = current_moving_index(sale_type, step_date, dealer, vendor, model)
        current_moving_index_df.loc[len(current_moving_index_df.index)] = [step_date, step_index]

    return current_moving_index_df


# --------------------Текущий год-год------------------------------
def current_year_year_index(
        sale_type: str,
        input_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None) -> float:
    result_df = sales
    date = pd.to_datetime(input_date)

    if dealer is not None:
        mask_dealer = result_df['dealer'] == dealer
        result_df = result_df[mask_dealer]

    if vendor is not None:
        mask_vendor = result_df['vendor'] == vendor
        result_df = result_df[mask_vendor]

    if model is not None:
        mask_model = result_df['model'] == model
        result_df = result_df[mask_model]

    mask_sale_type = result_df['sale_type'] == sale_type
    result_df = result_df[mask_sale_type]

    mask_date_current_month = (date - DateOffset(months=1) <= result_df['date']) & (result_df['date'] < date)
    result_df_current_month = result_df[mask_date_current_month].sort_values('date')

    mask_date_last_year_month = (date - DateOffset(years=1, months=1) <= result_df['date']) & (
            result_df['date'] < date - DateOffset(years=1))
    result_df_last_year_month = result_df[mask_date_last_year_month].sort_values('date')

    denominator = result_df_last_year_month.shape[0]

    numerator = result_df_current_month.shape[0]

    if denominator == 0:
        if numerator == 0:
            index = 1
        else:
            index = numerator
    else:
        index = numerator / denominator

    return index


def current_year_year_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    current_year_year_index_df = pd.DataFrame(
        {
            'date': [],
            'index': []
        }
    )
    current_year_year_index_df['date'] = pd.to_datetime(current_year_year_index_df['date'])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    for step_date in pd.date_range(start=start_date, end=end_date):
        step_index = current_year_year_index(sale_type, step_date, dealer, vendor, model)
        current_year_year_index_df.loc[len(current_year_year_index_df.index)] = [step_date, step_index]

    return current_year_year_index_df


# -------------------Длинный год-год--------------------
def long_year_year_index(
        sale_type: str,
        input_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None) -> float:
    result_df = sales
    date = pd.to_datetime(input_date)

    if dealer is not None:
        mask_dealer = result_df['dealer'] == dealer
        result_df = result_df[mask_dealer]

    if vendor is not None:
        mask_vendor = result_df['vendor'] == vendor
        result_df = result_df[mask_vendor]

    if model is not None:
        mask_model = result_df['model'] == model
        result_df = result_df[mask_model]

    mask_sale_type = result_df['sale_type'] == sale_type
    result_df = result_df[mask_sale_type]

    mask_date_this_year = (date - DateOffset(months=date.month - 1, days=date.day - 1) <= result_df['date']) & (
            result_df['date'] < date)
    result_df_this_year = result_df[mask_date_this_year].sort_values('date')

    mask_date_last_year = (date - DateOffset(years=1, months=date.month - 1, days=date.day - 1) <= result_df[
        'date']) & (result_df['date'] < date - DateOffset(years=1))
    result_df_last_year = result_df[mask_date_last_year].sort_values('date')

    denominator = result_df_last_year.shape[0]

    numerator = result_df_this_year.shape[0]

    if denominator == 0:
        if numerator == 0:
            index = 1
        else:
            index = numerator
    else:
        index = numerator / denominator

    return index


def long_year_year_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    long_year_year_index_df = pd.DataFrame(
        {
            'date': [],
            'index': []
        }
    )
    long_year_year_index_df['date'] = pd.to_datetime(long_year_year_index_df['date'])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    for step_date in pd.date_range(start=start_date, end=end_date):
        step_index = long_year_year_index(sale_type, step_date, dealer, vendor, model)
        long_year_year_index_df.loc[len(long_year_year_index_df.index)] = [step_date, step_index]

    return long_year_year_index_df
