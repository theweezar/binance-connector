# rule2_meanrev.py
import numpy as np
import pandas as pd


def apply(df: pd.DataFrame) -> pd.DataFrame:
    """Mean reversion: fade extremes beyond ±2σ"""
    df = df.copy()
    long_cond = (df["z_score"] < -2) & (df["ema_fast"] > df["ema_slow"])
    short_cond = (df["z_score"] > 2) & (df["ema_fast"] < df["ema_slow"])

    df["signal_rule2_meanrev"] = np.select([long_cond, short_cond], [1, -1], default=0)
    df["score_rule2_meanrev"] = df["z_score"].abs()

    df["signal_rule2_meanrev"] = np.where(
        (df["signal_rule2_meanrev"] != 0) & (df["signal_rule2_meanrev"].shift() == 0),
        df["signal_rule2_meanrev"],
        0,
    )

    return df
