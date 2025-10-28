# rule3_breakout.py
import numpy as np
import pandas as pd


def apply(df: pd.DataFrame) -> pd.DataFrame:
    """Breakout: close breaks above/below recent range"""
    df = df.copy()
    df["recent_high"] = df["high"].rolling(20).max()
    df["recent_low"] = df["low"].rolling(20).min()

    long_cond = df["close"] > df["recent_high"]
    short_cond = df["close"] < df["recent_low"]

    df["signal_rule3_breakout"] = np.select([long_cond, short_cond], [1, -1], default=0)
    df["score_rule3_breakout"] = (df["close"] - df["recent_low"]) / (
        df["recent_high"] - df["recent_low"]
    )

    df["signal_rule3_breakout"] = np.where(
        (df["signal_rule3_breakout"] != 0) & (df["signal_rule3_breakout"].shift() == 0),
        df["signal_rule3_breakout"],
        0,
    )
    return df
