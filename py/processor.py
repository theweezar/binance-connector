import ta.momentum
import ta.trend
import pandas
import ta


def process(frame: pandas.DataFrame):
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

    return frame
