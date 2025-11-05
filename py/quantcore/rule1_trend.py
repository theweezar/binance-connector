# rule1_trend.py
import numpy as np
import pandas as pd


def apply(df: pd.DataFrame) -> pd.DataFrame:
    """Trend-following rule: EMA crossover + ADX filter"""
    df = df.copy()
    long_cond = (df["ema_fast"] > df["ema_slow"]) & (df["adx"] > 25)
    short_cond = (df["ema_fast"] < df["ema_slow"]) & (df["adx"] > 25)

    df["signal_rule1_trend"] = np.select([long_cond, short_cond], [1, -1], default=0)
    df["score_rule1_trend"] = (df["adx"] - 25).clip(lower=0)

    df["signal_rule1_trend"] = np.where(
        (df["signal_rule1_trend"] != 0) & (df["signal_rule1_trend"].shift() == 0),
        df["signal_rule1_trend"],
        0,
    )

    return df
