# rule4_liquidity.py
import numpy as np
import pandas as pd


def apply(df: pd.DataFrame) -> pd.DataFrame:
    """Liquidity trap: price sweeps below/above BB then reverts"""
    df = df.copy()
    # long_cond = (df["low"] < df["bb_low"]) & (df["close"] > df["bb_low"])
    # short_cond = (df["high"] > df["bb_high"]) & (df["close"] < df["bb_high"])

    long_cond = (df["low"] < df["bb_low"]) & (df["close"] > df["open"])
    short_cond = (df["high"] > df["bb_high"]) & (df["close"] < df["open"])

    df["signal_rule4_liquidity"] = np.select(
        [long_cond, short_cond], [1, -1], default=0
    )
    df["score_rule4_liquidity"] = (df["close"] - df["rolling_mean"]).abs()

    df["signal_rule4_liquidity"] = np.where(
        (df["signal_rule4_liquidity"] != 0)
        & (df["signal_rule4_liquidity"].shift() == 0),
        df["signal_rule4_liquidity"],
        0,
    )
    return df
