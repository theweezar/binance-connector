import ta
import ta.momentum
import ta.trend
import file
import pandas


def rename_columns_1(dataframe: pandas.DataFrame, prefix: str = "") -> pandas.DataFrame:
    """
    Rename columns of the dataframe to lowercase.
    """
    dataframe.rename(
        columns={
            "Date": f"{prefix}_date",
            "Open": f"{prefix}_open",
            "High": f"{prefix}_high",
            "Low": f"{prefix}_low",
            "Close/Last": f"{prefix}_close",
        },
        inplace=True,
    )

    dataframe[f"{prefix}_open"] = dataframe[f"{prefix}_open"].astype(float)
    dataframe[f"{prefix}_high"] = dataframe[f"{prefix}_high"].astype(float)
    dataframe[f"{prefix}_low"] = dataframe[f"{prefix}_low"].astype(float)
    dataframe[f"{prefix}_close"] = dataframe[f"{prefix}_close"].astype(float)

    return dataframe


def rename_columns_2(dataframe: pandas.DataFrame, prefix: str = "") -> pandas.DataFrame:
    """
    Rename columns of the dataframe to lowercase.
    """
    dataframe.rename(
        columns={
            "Date": f"{prefix}_date",
            "Open": f"{prefix}_open",
            "High": f"{prefix}_high",
            "Low": f"{prefix}_low",
            "Price": f"{prefix}_close",
        },
        inplace=True,
    )
    dataframe.replace({r",": ""}, inplace=True, regex=True)

    dataframe[f"{prefix}_open"] = dataframe[f"{prefix}_open"].astype(float)
    dataframe[f"{prefix}_high"] = dataframe[f"{prefix}_high"].astype(float)
    dataframe[f"{prefix}_low"] = dataframe[f"{prefix}_low"].astype(float)
    dataframe[f"{prefix}_close"] = dataframe[f"{prefix}_close"].astype(float)

    return dataframe


def process(dataframe: pandas.DataFrame, prefix: str = "") -> pandas.DataFrame:
    """
    Processes the input DataFrame by calculating various technical indicators.

    Args:
        frame (pandas.DataFrame): The input DataFrame containing market data.

    Returns:
        pandas.DataFrame: The processed DataFrame with additional columns for technical indicators.
    """

    frame = dataframe.copy()

    _open = frame[f"{prefix}_open"]
    close = frame[f"{prefix}_close"]
    high = frame[f"{prefix}_high"]
    low = frame[f"{prefix}_low"]

    frame[f"{prefix}_price_change"] = close.pct_change()
    frame[f"{prefix}_volatility"] = close.rolling(10).std()

    rsi_6 = ta.momentum.rsi(close, 6)
    rsi_7 = ta.momentum.rsi(close, 7)
    rsi_9 = ta.momentum.rsi(close, 9)
    rsi_12 = ta.momentum.rsi(close, 12)
    rsi_14 = ta.momentum.rsi(close, 14)
    rsi_30 = ta.momentum.rsi(close, 30)
    ema_34 = ta.trend.ema_indicator(close, 34)
    ema_89 = ta.trend.ema_indicator(close, 89)

    frame[f"{prefix}_rsi_6"] = rsi_6
    frame[f"{prefix}_rsi_7"] = rsi_7
    frame[f"{prefix}_rsi_9"] = rsi_9
    frame[f"{prefix}_rsi_12"] = rsi_12
    frame[f"{prefix}_rsi_14"] = rsi_14
    frame[f"{prefix}_rsi_30"] = rsi_30
    frame[f"{prefix}_ema_34"] = ema_34
    frame[f"{prefix}_ema_89"] = ema_89

    frame[f"{prefix}_ema_trend"] = ema_34 - ema_89

    ema_12 = ta.trend.ema_indicator(close, 12)
    ema_26 = ta.trend.ema_indicator(close, 26)
    macd = ema_12 - ema_26

    frame[f"{prefix}_macd"] = macd
    frame[f"{prefix}_macd_signal"] = ta.trend.ema_indicator(macd, 9)
    frame[f"{prefix}_adx_14"] = ta.trend.ADXIndicator(high, low, close).adx()

    frame[f"{prefix}_type"] = (close >= _open).astype(int).astype(str)
    frame[f"{prefix}_next_type"] = frame[f"{prefix}_type"].shift(-1)

    return frame


sp500 = file.get_source("ignore/stock/S&P 500_HistoricalData_1744300674147.csv")
nasdaq = file.get_source("ignore/stock/Nasdaq_HistoricalData_1744301075920.csv")
gold = file.get_source("ignore/stock/Gold Futures Historical Data.csv")

sp500_frame = rename_columns_1(sp500["dataframe"], "sp500")
nasdaq_frame = rename_columns_1(nasdaq["dataframe"], "nasdaq")
gold_frame = rename_columns_2(gold["dataframe"], "gold")

sp500_frame = process(sp500_frame, "sp500")
nasdaq_frame = process(nasdaq_frame, "nasdaq")
gold_frame = process(gold_frame, "gold")

combine = pandas.DataFrame()

combine = combine.join(sp500_frame)
combine = combine.join(nasdaq_frame)
combine = combine.join(gold_frame)

file.write(
    "ignore/stock/ta/S&P 500_HistoricalData_1744300674147.csv",
    sp500_frame.to_csv(index_label="index"),
)
file.write(
    "ignore/stock/ta/Nasdaq_HistoricalData_1744301075920.csv",
    nasdaq_frame.to_csv(index_label="index"),
)
file.write(
    "ignore/stock/ta/Gold Futures Historical Data.csv",
    gold_frame.to_csv(index_label="index"),
)
file.write(
    "ignore/stock/ta/stock_combination.csv",
    combine.to_csv(index_label="index"),
)
