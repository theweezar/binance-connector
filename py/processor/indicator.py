import ta.momentum
import ta.trend
import pandas
import ta


def apply(frame: pandas.DataFrame):
    """
    Apply more technical indicators to the input DataFrame.

    Args:
        frame (pandas.DataFrame): The input DataFrame containing market data.

    Returns:
        pandas.DataFrame: The processed DataFrame with additional columns for technical indicators.
    """
    close = frame["close"]
    high = frame["high"]
    low = frame["low"]

    frame["price_change"] = close.pct_change()
    frame["volatility"] = close.rolling(10).std()

    rsi_6 = ta.momentum.rsi(close, 6)
    rsi_7 = ta.momentum.rsi(close, 7)
    rsi_9 = ta.momentum.rsi(close, 9)
    rsi_12 = ta.momentum.rsi(close, 12)
    rsi_14 = ta.momentum.rsi(close, 14)
    rsi_30 = ta.momentum.rsi(close, 30)
    ema_34 = ta.trend.ema_indicator(close, 34)
    ema_89 = ta.trend.ema_indicator(close, 89)

    frame["rsi_6"] = rsi_6
    frame["rsi_7"] = rsi_7
    frame["rsi_9"] = rsi_9
    frame["rsi_12"] = rsi_12
    frame["rsi_14"] = rsi_14
    frame["rsi_30"] = rsi_30
    frame["ema_34"] = ema_34
    frame["ema_89"] = ema_89

    ema_trend = ema_34 - ema_89

    frame["ema_trend"] = ema_trend

    ema_12 = ta.trend.ema_indicator(close, 12)
    ema_26 = ta.trend.ema_indicator(close, 26)
    macd = ema_12 - ema_26

    frame["macd"] = macd
    frame["macd_signal"] = ta.trend.ema_indicator(macd, 9)

    frame["adx_14"] = ta.trend.ADXIndicator(high, low, close).adx()

    frame["next_type"] = frame["type"].shift(-1)

    return frame


def calc_price_if_reverse_rsi_reach(
    prices: pandas.Series, desired_rsi: float, period: int, price_offset: int
) -> float:
    """
    Calculate the price if RSI reaches a desired value.

    Args:
        prices (pandas.Series): The input price series.
        desired_rsi (float): The desired RSI value.
        period (int): The RSI period.
        price_offset (int): The price offset.

    Returns:
        float: The price at which the RSI reaches the desired value.
    """

    this_prices = prices.copy()
    current_rsi = ta.momentum.rsi(this_prices, period)

    length = len(current_rsi)

    if current_rsi[length - 1] >= desired_rsi:
        return this_prices[length - 1]

    this_rsi = current_rsi[length - 1]

    while this_rsi < desired_rsi:
        this_prices[length - 1] = this_prices[length - 1] + price_offset
        rsi_add_offset = ta.momentum.rsi(this_prices, period)
        this_rsi = rsi_add_offset[length - 1]

    return this_prices[length - 1]


def calc_price_if_reverse_rsi_drop(
    prices: pandas.Series, desired_rsi: float, period: int, price_offset: int
) -> float:
    """
    Calculate the price if RSI drops below a desired value.

    Args:
        prices (pandas.Series): The input price series.
        desired_rsi (float): The desired RSI value.
        period (int): The RSI period.
        price_offset (int): The price offset.

    Returns:
        float: The price at which the RSI drops below the desired value.
    """

    this_prices = prices.copy()
    current_rsi = ta.momentum.rsi(this_prices, period)

    length = len(current_rsi)

    if current_rsi[length - 1] <= desired_rsi:
        return this_prices[length - 1]

    this_rsi = current_rsi[length - 1]

    while this_rsi > desired_rsi:
        this_prices[length - 1] = this_prices[length - 1] + price_offset
        rsi_add_offset = ta.momentum.rsi(this_prices, period)
        this_rsi = rsi_add_offset[length - 1]

    return this_prices[length - 1]
