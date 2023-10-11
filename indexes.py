import pandas as pd

sales = pd.read_csv('./sale_data.csv', index_col=0)
sales['date'] = pd.to_datetime(sales['date'])


def _index(numerator, denominator):  # Считает индекс в зависимости от числителя и знаменателя
    if denominator == 0:
        index = 100 if numerator != 0 else 0
    else:
        index = (numerator / denominator - 1) * 100

    return index


# ---------------Мгновенный-скользящий---------------
# можно выбирать данные >= 7д начала дф
def instant_moving_index(result_df, input_date) -> float:  # result_df уже обработанный отсортированный датафрейм

    mask = (result_df['date'] >= input_date - pd.DateOffset(days=6)) & (result_df['date'] < input_date)
    result_df = result_df[mask]

    numerator = len(result_df[result_df['date'] >= input_date - pd.DateOffset(days=3)])
    denominator = len(result_df) - numerator

    return _index(numerator, denominator)


def instant_moving_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    mask = (sales['sale_type'] == sale_type)
    if dealer is not None:
        mask &= (sales['dealer'] == dealer)
    if vendor is not None:
        mask &= (sales['vendor'] == vendor)
    if model is not None:
        mask &= (sales['model'] == model)
    result_df = sales[mask]

    date_range = pd.date_range(start=start_date, end=end_date)
    index_values = [instant_moving_index(result_df, step_date) for step_date in date_range]
    instant_moving_index_array = pd.DataFrame({'date': date_range, 'index': index_values})

    return instant_moving_index_array


# ---------------Мгновенный-год-год---------------
# можно выбирать данные >= 1г 4д начала дф
def instant_year_year_index(result_df, input_date) -> float:
    mask_current_year = (input_date - pd.DateOffset(days=3) <= result_df['date']) & (result_df['date'] < input_date)
    result_df_current_year = result_df[mask_current_year]

    mask_last_year = (input_date - pd.DateOffset(years=1, days=3) <= result_df['date']) & (
            result_df['date'] < input_date - pd.DateOffset(years=1))
    result_df_last_year = result_df[mask_last_year]

    denominator = len(result_df_last_year)
    numerator = len(result_df_current_year)

    return _index(numerator, denominator)


def instant_year_year_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    mask = (sales['sale_type'] == sale_type)
    if dealer is not None:
        mask &= (sales['dealer'] == dealer)
    if vendor is not None:
        mask &= (sales['vendor'] == vendor)
    if model is not None:
        mask &= (sales['model'] == model)
    result_df = sales[mask]

    date_range = pd.date_range(start=start_date, end=end_date)
    index_values = [instant_year_year_index(result_df, step_date) for step_date in date_range]
    instant_y_y_index_array = pd.DataFrame({'date': date_range, 'index': index_values})

    return instant_y_y_index_array


# ---------------Текущий-скользящий---------------
# можно выбирать данные >= 61д начала дф
def current_moving_index(result_df, input_date) -> float:
    mask = (input_date - pd.DateOffset(months=2) <= result_df['date']) & (result_df['date'] < input_date)
    result_df = result_df[mask]

    numerator = len(result_df[result_df['date'] >= input_date - pd.DateOffset(months=1)])
    denominator = len(result_df) - numerator

    return _index(numerator, denominator)


def current_moving_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    mask = (sales['sale_type'] == sale_type)
    if dealer is not None:
        mask &= (sales['dealer'] == dealer)
    if vendor is not None:
        mask &= (sales['vendor'] == vendor)
    if model is not None:
        mask &= (sales['model'] == model)
    result_df = sales[mask]

    date_range = pd.date_range(start=start_date, end=end_date)
    index_values = [current_moving_index(result_df, step_date) for step_date in date_range]
    current_moving_index_array = pd.DataFrame({'date': date_range, 'index': index_values})

    return current_moving_index_array


# ---------------Текущий-год-год---------------
# можно выбирать данные >= 1г 1м
def current_year_year_index(result_df, input_date) -> float:
    mask_current_month = (input_date - pd.DateOffset(months=1) <= result_df['date']) & (result_df['date'] < input_date)
    result_df_current_month = result_df[mask_current_month]

    mask_last_year_month = (input_date - pd.DateOffset(years=1, months=1) <= result_df['date']) & (
            result_df['date'] < input_date - pd.DateOffset(years=1))
    result_df_last_year_month = result_df[mask_last_year_month]

    denominator = len(result_df_last_year_month)
    numerator = len(result_df_current_month)

    return _index(numerator, denominator)


def current_year_year_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    mask = (sales['sale_type'] == sale_type)
    if dealer is not None:
        mask &= (sales['dealer'] == dealer)
    if vendor is not None:
        mask &= (sales['vendor'] == vendor)
    if model is not None:
        mask &= (sales['model'] == model)
    result_df = sales[mask]

    date_range = pd.date_range(start=start_date, end=end_date)
    index_values = [current_year_year_index(result_df, step_date) for step_date in date_range]
    current_y_y_index_array = pd.DataFrame({'date': date_range, 'index': index_values})

    return current_y_y_index_array


# ---------------Длинный-скользящий---------------
# можно выбирать данные >= 2г 1д начала дф
def long_moving_index(result_df, input_date) -> float:
    mask = (input_date - pd.DateOffset(years=2) <= result_df['date']) & (result_df['date'] < input_date)
    result_df = result_df[mask]

    numerator = len(result_df[result_df['date'] >= input_date - pd.DateOffset(years=1)])
    denominator = len(result_df) - numerator

    return _index(numerator, denominator)


def long_moving_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    mask = (sales['sale_type'] == sale_type)
    if dealer is not None:
        mask &= (sales['dealer'] == dealer)
    if vendor is not None:
        mask &= (sales['vendor'] == vendor)
    if model is not None:
        mask &= (sales['model'] == model)
    result_df = sales[mask]

    date_range = pd.date_range(start=start_date, end=end_date)
    index_values = [long_moving_index(result_df, step_date) for step_date in date_range]
    long_moving_index_array = pd.DataFrame({'date': date_range, 'index': index_values})

    return long_moving_index_array


# ---------------Длинный-год-год---------------
def long_year_year_index(result_df, input_date) -> float:
    mask_this_year = (input_date - pd.DateOffset(months=input_date.month - 1, days=input_date.day - 1) <=
                      result_df['date']) & (result_df['date'] < input_date)
    result_df_this_year = result_df[mask_this_year]

    mask_last_year = (input_date - pd.DateOffset(years=1, months=input_date.month - 1, days=input_date.day - 1) <=
                      result_df['date']) & (result_df['date'] < input_date - pd.DateOffset(years=1))
    result_df_last_year = result_df[mask_last_year]

    denominator = len(result_df_last_year)
    numerator = len(result_df_this_year)

    return _index(numerator, denominator)


def long_year_year_index_interval(
        sale_type: str,
        start_date: str,
        end_date: str,
        dealer: str = None,
        vendor: str = None,
        model: str = None
):
    mask = (sales['sale_type'] == sale_type)
    if dealer is not None:
        mask &= (sales['dealer'] == dealer)
    if vendor is not None:
        mask &= (sales['vendor'] == vendor)
    if model is not None:
        mask &= (sales['model'] == model)
    result_df = sales[mask]

    date_range = pd.date_range(start=start_date, end=end_date)
    index_values = [long_year_year_index(result_df, step_date) for step_date in date_range]
    long_y_y_index_array = pd.DataFrame({'date': date_range, 'index': index_values})

    return long_y_y_index_array
