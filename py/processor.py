import ta.momentum
import ta.trend
import pandas
import ta
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def process(frame: pandas.DataFrame):
    """
    Processes the input DataFrame by calculating various technical indicators.

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
    symbol = frame["symbol"][0]
    offsets = {
        "BTCUSDT": 75,
        "LTCUSDT": 1,
        "ETHUSDT": 10,
        "XRPUSDT": 0.1,
        "BNBUSDT": 1,
        "DOGEUSDT": 0.01,
        "PEPEUSDT": 0.01,
        "ADAUSDT": 0.01,
    }

    frame["ema_trend"] = ema_trend
    frame["ema_34_x_ema_89"] = (
        (ema_trend.abs() <= offsets[symbol]).astype(int).astype(str)
    )

    ema_12 = ta.trend.ema_indicator(close, 12)
    ema_26 = ta.trend.ema_indicator(close, 26)
    macd = ema_12 - ema_26

    frame["macd"] = macd
    frame["macd_signal"] = ta.trend.ema_indicator(macd, 9)

    frame["adx_14"] = ta.trend.ADXIndicator(high, low, close).adx()

    frame["next_type"] = frame["type"].shift(-1)

    return frame


def apply_grok3_solution(dataframe: pandas.DataFrame):
    """
    Applies the Grok3 scaling solution to the input DataFrame.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame containing market data.

    Returns:
        pandas.DataFrame: The scaled DataFrame with selected features.
    """
    print("Using Grok3 solution")
    standard_scaler = StandardScaler()
    minmax_scaler = MinMaxScaler()
    data = dataframe.copy()

    standard_x_features = data[
        [
            "close",
            "vol",
            "ema_34",
            "ema_89",
        ]
    ]
    standard_x_features = pandas.DataFrame(
        standard_scaler.fit_transform(standard_x_features.values),
        columns=standard_x_features.columns.values,
    )

    minmax_x_features = data[
        [
            "ema_trend",
            "rsi_6",
            "rsi_9",
            "macd",
            "macd_signal",
            "adx_14",
        ]
    ]
    minmax_x_features = pandas.DataFrame(
        minmax_scaler.fit_transform(minmax_x_features.values),
        columns=minmax_x_features.columns.values,
    )

    X_scaled = standard_x_features.join(minmax_x_features)

    return X_scaled


def apply_chatgpt_solution(dataframe: pandas.DataFrame):
    """
    Applies the ChatGPT scaling solution to the input DataFrame.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame containing market data.

    Returns:
        pandas.DataFrame: The scaled DataFrame with selected features.
    """
    print("Using ChatGPT solution")
    data = dataframe.copy()

    # Raw X values
    x_features = data[
        [
            # "close",
            # "vol",
            "ema_trend",
            "rsi_6",
            "rsi_9",
            "ema_34",
            "ema_89",
            "macd",
            "macd_signal",
            "adx_14",
        ]
    ]

    # Initialize StandardScaler
    scaler = StandardScaler()

    # Scale the dataset
    X_scaled = scaler.fit_transform(x_features.values)

    return pandas.DataFrame(X_scaled)


def preprocessing_data(
    dataframe: pandas.DataFrame, dropna: bool = False
) -> tuple[pandas.DataFrame, pandas.DataFrame, str]:
    """
    Preprocesses the data for model training.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        dropna (bool): Whether to drop NaN values from the DataFrame.

    Returns:
        tuple: A tuple containing the scaled features (X), target (y), and symbol.
    """
    data = dataframe.copy()
    symbol = data["symbol"][0]

    if dropna is True:
        print("Dropping NaN values")
        data.dropna(inplace=True)

    # X_scaled = apply_grok3_solution(data)
    X_scaled = apply_chatgpt_solution(data)

    # Binary classification -> Up/Down -> raw y values
    y_target = (data["next_type"] == "U").astype(int)

    return X_scaled, y_target, symbol
