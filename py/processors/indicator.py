import ta.momentum
import ta.trend
import ta.volume
import pandas
import ta


def add_rsi(df: pandas.DataFrame, window: int, column_name: str = "close"):
    """
    Add Relative Strength Index (RSI) to the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        window (int): The window for the RSI.
        column_name (str): The column to calculate the RSI on.

    Returns:
        pandas.DataFrame: The DataFrame with the RSI added.
    """
    df_col_name = f"rsi_{window}"
    if column_name != "close":
        df_col_name = f"rsi_{window}_{column_name}"
    df[df_col_name] = ta.momentum.rsi(df[column_name], window)
    return df


def add_ema(df: pandas.DataFrame, window: int, column_name: str = "close"):
    """
    Add Exponential Moving Average (EMA) to the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        period (int): The period for the EMA.
        column_name (str): The column to calculate the EMA on.

    Returns:
        pandas.DataFrame: The DataFrame with the EMA added.
    """
    df[f"ema_{window}"] = ta.trend.ema_indicator(df[column_name], window)
    return df


def add_ma(df: pandas.DataFrame, window: int, column_name: str = "close"):
    """
    Add Simple Moving Average (SMA) to the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        period (int): The period for the SMA.
        column_name (str): The column to calculate the SMA on.

    Returns:
        pandas.DataFrame: The DataFrame with the SMA added.
    """
    df[f"ma_{window}"] = ta.trend.sma_indicator(df[column_name], window)
    return df


def add_macd(df: pandas.DataFrame, column_name: str = "close"):
    """
    Add MACD (Moving Average Convergence Divergence) to the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        column_name (str): The column to calculate the MACD on.

    Returns:
        pandas.DataFrame: The DataFrame with the MACD added.
    """
    ema_12 = ta.trend.ema_indicator(df[column_name], 12)
    ema_26 = ta.trend.ema_indicator(df[column_name], 26)
    macd = ema_12 - ema_26
    df["macd"] = macd
    df["macd_signal"] = ta.trend.ema_indicator(macd, 9)
    return df


def add_adx(df: pandas.DataFrame, window: int = 14):
    """
    Add ADX (Average Directional Index) to the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.

    Returns:
        pandas.DataFrame: The DataFrame with the ADX added.
    """
    adx = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=window)
    df[f"adx_{window}"] = adx.adx()
    df[f"+di_{window}"] = adx.adx_pos()
    df[f"-di_{window}"] = adx.adx_neg()
    return df


def add_stochastic(df: pandas.DataFrame, window: int = 14):
    """
    Add Stochastic Oscillator to the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        window (int): The window for the Stochastic Oscillator.

    Returns:
        pandas.DataFrame: The DataFrame with the Stochastic Oscillator added.
    """
    stoch = ta.momentum.StochasticOscillator(
        df["high"], df["low"], df["close"], window=window
    )
    df[f"stoch_{window}"] = stoch.stoch()
    df[f"stoch_signal_{window}"] = stoch.stoch_signal()
    return df


def detect_support_resistance(df: pandas.DataFrame, window: int = 20):
    """
    Detect support and resistance levels in the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        window (int): The window size for detecting support and resistance.

    Returns:
        pandas.DataFrame: The DataFrame with support and resistance levels added.
    """

    df["support"] = "-"
    df["resistance"] = "-"
    df["support"] = df["low"][
        (df["low"].shift(window) > df["low"]) & (df["low"].shift(-window) > df["low"])
    ]
    df["resistance"] = df["high"][
        (df["high"].shift(window) < df["high"])
        & (df["high"].shift(-window) < df["high"])
    ]
    return df


def apply(df: pandas.DataFrame):
    """
    Apply more technical indicators to the input DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame containing market data.

    Returns:
        pandas.DataFrame: The processed DataFrame with additional columns for technical indicators.
    """
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volumne = df["vol"]

    df["price_change"] = close.pct_change()
    df["volatility"] = close.rolling(10).std()

    # Calculate RSI for different periods
    df = add_rsi(df, 6, "close")
    df = add_rsi(df, 6, "high")
    df = add_rsi(df, 6, "low")

    df = add_rsi(df, 9, "close")
    df = add_rsi(df, 9, "high")
    df = add_rsi(df, 9, "low")

    # df = add_rsi(df, 14, "close")

    # Calculate EMA and SMA
    df = add_ema(df, 9, "close")
    df = add_ema(df, 21, "close")
    # df = add_ema(df, 34, "close")
    # df = add_ema(df, 50, "close")
    # df = add_ema(df, 89, "close")
    # df = add_ma(df, 9, "close")
    # df = add_ma(df, 20, "close")
    # df = add_ma(df, 21, "close")
    # df = add_ma(df, 50, "close")

    # ema_trend = ema_34 - ema_89
    # df["ema_trend"] = ema_trend

    # df = add_macd(df, "close")
    # df = add_adx(df, 5)
    # df = add_adx(df, 6)
    # df = add_adx(df, 14)

    # Donchian Channel (20-period)
    # df["donchian_high"] = high.rolling(window=20).max()
    # df["donchian_low"] = low.rolling(window=20).min()

    # df["vwap"] = ta.volume.VolumeWeightedAveragePrice(
    #     high=high, low=low, close=close, volume=volumne
    # ).vwap

    # df["next_type"] = df["type"].shift(-1)

    df = detect_support_resistance(df, window=21)

    df = add_stochastic(df, 5)

    return df


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
