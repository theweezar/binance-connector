# indicator.py
import pandas as pd
import ta
import ta.volatility
import ta.trend
import ta.momentum


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Moving averages
    df["ema_fast"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema_slow"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()

    # Volatility indicators
    bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()

    # Trend strength
    df["adx"] = ta.trend.ADXIndicator(
        df["high"], df["low"], df["close"], window=14
    ).adx()

    # Mean reversion (Z-score)
    df["rolling_mean"] = df["close"].rolling(20).mean()
    df["rolling_std"] = df["close"].rolling(20).std()
    df["z_score"] = (df["close"] - df["rolling_mean"]) / df["rolling_std"]

    # ATR (volatility measure)
    df["atr"] = ta.volatility.AverageTrueRange(
        df["high"], df["low"], df["close"], window=14
    ).average_true_range()

    df["ema_5"] = ta.trend.ema_indicator(df["close"], 5)
    df["ema_20"] = ta.trend.ema_indicator(df["close"], 20)

    df["rsi_9"] = ta.momentum.rsi(df["close"], 9)

    return df
