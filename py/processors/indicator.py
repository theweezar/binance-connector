import ta.momentum
import ta.trend
import ta.volume
import pandas
import ta


def add_rsi(frame: pandas.DataFrame, window: int, column_name: str = "close"):
    """
    Add Relative Strength Index (RSI) to the DataFrame.

    Args:
        frame (pandas.DataFrame): The input DataFrame.
        window (int): The window for the RSI.
        column_name (str): The column to calculate the RSI on.

    Returns:
        pandas.DataFrame: The DataFrame with the RSI added.
    """
    df_col_name = f"rsi_{window}"
    if column_name != "close":
        df_col_name = f"rsi_{window}_{column_name}"
    frame[df_col_name] = ta.momentum.rsi(frame[column_name], window)
    return frame


def add_ema(frame: pandas.DataFrame, window: int, column_name: str = "close"):
    """
    Add Exponential Moving Average (EMA) to the DataFrame.

    Args:
        frame (pandas.DataFrame): The input DataFrame.
        period (int): The period for the EMA.
        column_name (str): The column to calculate the EMA on.

    Returns:
        pandas.DataFrame: The DataFrame with the EMA added.
    """
    frame[f"ema_{window}"] = ta.trend.ema_indicator(frame[column_name], window)
    return frame


def add_ma(frame: pandas.DataFrame, window: int, column_name: str = "close"):
    """
    Add Simple Moving Average (SMA) to the DataFrame.

    Args:
        frame (pandas.DataFrame): The input DataFrame.
        period (int): The period for the SMA.
        column_name (str): The column to calculate the SMA on.

    Returns:
        pandas.DataFrame: The DataFrame with the SMA added.
    """
    frame[f"ma_{window}"] = ta.trend.sma_indicator(frame[column_name], window)
    return frame


def add_macd(frame: pandas.DataFrame, column_name: str = "close"):
    """
    Add MACD (Moving Average Convergence Divergence) to the DataFrame.

    Args:
        frame (pandas.DataFrame): The input DataFrame.
        column_name (str): The column to calculate the MACD on.

    Returns:
        pandas.DataFrame: The DataFrame with the MACD added.
    """
    ema_12 = ta.trend.ema_indicator(frame[column_name], 12)
    ema_26 = ta.trend.ema_indicator(frame[column_name], 26)
    macd = ema_12 - ema_26
    frame["macd"] = macd
    frame["macd_signal"] = ta.trend.ema_indicator(macd, 9)
    return frame


def add_adx(frame: pandas.DataFrame, window: int = 14):
    """
    Add ADX (Average Directional Index) to the DataFrame.

    Args:
        frame (pandas.DataFrame): The input DataFrame.

    Returns:
        pandas.DataFrame: The DataFrame with the ADX added.
    """
    adx = ta.trend.ADXIndicator(
        frame["high"], frame["low"], frame["close"], window=window
    )
    frame[f"adx_{window}"] = adx.adx()
    frame[f"+di_{window}"] = adx.adx_pos()
    frame[f"-di_{window}"] = adx.adx_neg()
    return frame


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
    volumne = frame["vol"]

    frame["price_change"] = close.pct_change()
    frame["volatility"] = close.rolling(10).std()

    # Calculate RSI for different periods
    frame = add_rsi(frame, 5, "close")
    frame = add_rsi(frame, 5, "high")
    frame = add_rsi(frame, 5, "low")

    frame = add_rsi(frame, 6, "close")
    frame = add_rsi(frame, 6, "high")
    frame = add_rsi(frame, 6, "low")

    frame = add_rsi(frame, 14, "close")

    # Calculate EMA and SMA
    frame = add_ema(frame, 9, "close")
    frame = add_ema(frame, 21, "close")
    # frame = add_ema(frame, 34, "close")
    # frame = add_ema(frame, 50, "close")
    # frame = add_ema(frame, 89, "close")
    frame = add_ma(frame, 9, "close")
    # frame = add_ma(frame, 20, "close")
    frame = add_ma(frame, 21, "close")
    # frame = add_ma(frame, 50, "close")

    # ema_trend = ema_34 - ema_89
    # frame["ema_trend"] = ema_trend

    frame = add_macd(frame, "close")
    frame = add_adx(frame, 5)
    frame = add_adx(frame, 6)
    frame = add_adx(frame, 14)

    # Donchian Channel (20-period)
    # frame["donchian_high"] = high.rolling(window=20).max()
    # frame["donchian_low"] = low.rolling(window=20).min()

    # frame["vwap"] = ta.volume.VolumeWeightedAveragePrice(
    #     high=high, low=low, close=close, volume=volumne
    # ).vwap

    # frame["next_type"] = frame["type"].shift(-1)

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
