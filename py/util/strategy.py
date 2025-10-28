import pandas as pd
import numpy as np
from scipy.signal import argrelextrema


def select_short_position_maximum_of(
    df: pd.DataFrame, column_name: str, window: int = 5
):
    """
    For each rolling window of 'steps', keep only the short position (position==0)
    with the maximum value in the specified column, set others to "-".

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_name (str): Column to find the maximum value for short positions.
        window (int): Size of the rolling window.

    Returns:
        pd.DataFrame: DataFrame with only the maximum short position kept per window.
    """
    cp_df = df.copy()

    for i in range(0, len(cp_df) - window + 1):
        # Select group by window
        group_by_window = cp_df[i : i + window]
        # Select short positions in group
        group_has_short = group_by_window[group_by_window["position"] == 0]

        if group_has_short.empty:
            continue

        max_value = group_has_short[column_name].max()
        max_index = group_has_short[group_has_short[column_name] == max_value].index[0]
        cp_df.loc[group_has_short.index, "position"] = "-"
        cp_df.loc[max_index, "position"] = 0

    return cp_df


def select_long_position_minimum_of(
    df: pd.DataFrame, column_name: str, window: int = 5
):
    """
    For each rolling window of 'window', keep only the long position (position==1)
    with the minimum value in the specified column, set others to "-".

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_name (str): Column to find the minimum value for long positions.
        window (int): Size of the rolling window.

    Returns:
        pd.DataFrame: DataFrame with only the minimum long position kept per window.
    """
    cp_df = df.copy()

    for i in range(0, len(cp_df) - window + 1):
        # Select group by window
        group_by_window = cp_df[i : i + window]
        # Select long positions in group
        group_has_long = group_by_window[group_by_window["position"] == 1]

        if group_has_long.empty:
            continue

        min_value = group_has_long[column_name].min()
        min_index = group_has_long[group_has_long[column_name] == min_value].index[0]
        cp_df.loc[group_has_long.index, "position"] = "-"
        cp_df.loc[min_index, "position"] = 1

    return cp_df


def apply_rsi(df: pd.DataFrame, window: int = 5):
    """
    Apply RSI-based trading signals to the DataFrame.
    Args:
        df (pd.DataFrame): DataFrame containing market data with RSI columns.
        window (int): RSI window size.
    Returns:
        pd.DataFrame: DataFrame with a new 'position' column indicating trading signals.
    """

    low_column = f"rsi_{window}_low"
    high_column = f"rsi_{window}_high"

    long_mask = (df[low_column] < 20) & (df[low_column] > 4)
    df.loc[long_mask, "position"] = 1

    short_mask = (df[high_column] > 80) & (df[high_column] < 95)
    df.loc[short_mask, "position"] = 0

    sensitive_long_mask = df[low_column] < 4
    df.loc[sensitive_long_mask, "sensitive_position"] = 1

    sensitive_short_mask = df[high_column] > 95
    df.loc[sensitive_short_mask, "sensitive_position"] = 0

    return df


def is_bullish_engulfing(row: pd.Series, prev_row: pd.Series) -> bool:
    """
    Check if the current row is a bullish engulfing pattern compared to the previous row.
    Args:
        row (pd.Series): Current row of the DataFrame.
        prev_row (pd.Series): Previous row of the DataFrame.
    Returns:
        bool: True if the current row is a bullish engulfing pattern, False otherwise.
    """
    return (
        prev_row["close"] < prev_row["open"]
        and row["close"] > row["open"]
        and row["close"] > prev_row["open"]
        and row["open"] < prev_row["close"]
    )


def is_bearish_engulfing(row: pd.Series, prev_row: pd.Series) -> bool:
    """
    Check if the current row is a bearish engulfing pattern compared to the previous row.
    Args:
        row (pd.Series): Current row of the DataFrame.
        prev_row (pd.Series): Previous row of the DataFrame.
    Returns:
        bool: True if the current row is a bearish engulfing pattern, False otherwise.
    """
    return (
        prev_row["close"] > prev_row["open"]
        and row["close"] < row["open"]
        and row["open"] > prev_row["close"]
        and row["close"] < prev_row["open"]
    )


def cross_up(
    prev_col: pd.Series, curr_col: pd.Series, subject_name: str, object_name: str
):
    """
    Check if the current column crosses above the previous column.
    Args:
        prev_col (pd.Series): Previous column.
        curr_col (pd.Series): Current column.
        subject_name (str): Name of the subject series.
        object_name (str): Name of the object series.
    Returns:
        bool: True if current crosses above previous, False otherwise.
    """
    return (
        prev_col[subject_name] < prev_col[object_name]
        and curr_col[subject_name] > curr_col[object_name]
    )


def cross_down(
    prev_col: pd.Series, curr_col: pd.Series, subject_name: str, object_name: str
):
    """
    Check if the current column crosses below the previous column.
    Args:
        prev_col (pd.Series): Previous column.
        curr_col (pd.Series): Current column.
        subject_name (str): Name of the subject series.
        object_name (str): Name of the object series.
    Returns:
        bool: True if current crosses below previous, False otherwise.
    """
    return (
        prev_col[subject_name] > prev_col[object_name]
        and curr_col[subject_name] < curr_col[object_name]
    )


def apply_engulfing(df: pd.DataFrame):
    """
    Generate trading signals based on EMA crossovers and engulfing patterns.
    Args:
        df (pd.DataFrame): DataFrame containing market data with EMA columns.
    Returns:
        pd.DataFrame: DataFrame with a new 'position' column indicating trading signals.
    """

    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        # Example: EMA crossover + bullish engulfing + RSI confirmation
        bullish_cross = cross_up(prev, curr, "ema_9", "ema_21")
        bearish_cross = cross_down(prev, curr, "ema_9", "ema_21")
        bullish_engulf = is_bullish_engulfing(curr, prev)
        bearish_engulf = is_bearish_engulfing(curr, prev)
        # Long entry conditions
        if bullish_cross and bullish_engulf:
            df.at[df.index[i], "position"] = 1
        # Short entry conditions
        if bearish_cross and bearish_engulf:
            df.at[df.index[i], "position"] = 0
    return df


def calc_trend_polyfit(df: pd.DataFrame, col: str, steps: int = 3):
    """
    Calculate the trend of a given column using polynomial fitting.
    Args:
        df (pd.DataFrame): DataFrame containing the data.
        col (str): Column name to calculate the trend for.
        steps (int): Number of steps to consider for the trend calculation.
    Returns:
        list: List of trend directions ("up", "down", "flat") for each step
    """
    trend = [None] * steps
    series = df[col].values
    for i in range(steps, len(series)):
        y = series[(i - steps) : i + 1]
        x = np.arange(steps + 1)
        slope, intercept = np.polyfit(x, y, 1)
        # You can adjust the threshold for "flat" trend if desired
        if slope > 1e-6:
            trend.append("up")
        elif slope < -1e-6:
            trend.append("down")
        else:
            trend.append("flat")
    return trend


def apply_rsi_adx_trends(df: pd.DataFrame, method: str = "polyfit"):
    """
    Apply RSI and ADX trends to the DataFrame to set trading positions.
    Signal logic:
    When RSI goes down and ADX goes up => price about to rise (long signal)
    When RSI goes up and ADX goes down => price about to drop (short signal).
    Args:
        df (pd.DataFrame): DataFrame containing market data with RSI and ADX columns.
        method (str): Method to calculate trends, e.g., "polyfit".
    Returns:
        pd.DataFrame: DataFrame with new columns for RSI and ADX trends.
    """
    if method == "polyfit":
        df["rsi_trend"] = calc_trend_polyfit(df, "rsi_6", steps=6)
        df["adx_trend"] = calc_trend_polyfit(df, "adx_6", steps=6)

    long_mask = (df["rsi_trend"] == "down") & (df["adx_trend"] == "up")
    short_mask = (df["rsi_trend"] == "up") & (df["adx_trend"] == "down")

    df.loc[long_mask, "position"] = 1
    df.loc[short_mask, "position"] = 0

    return df


def find_local_extrema(series: pd.Series, order: int = 5, mode: str = "max"):
    if mode == "max":
        idx = argrelextrema(series.values, np.greater_equal, order=order)[0]
    else:
        idx = argrelextrema(series.values, np.less_equal, order=order)[0]
    return idx


def detect_rsi_divergence(df: pd.DataFrame, order: int):
    # Find swing highs and lows in price

    length = len(df)
    latest_100 = df[length - 100 : length]

    highs = find_local_extrema(latest_100["close"], order=order, mode="max")
    lows = find_local_extrema(latest_100["close"], order=order, mode="min")

    highs = highs + (length - 100)
    lows = lows + (length - 100)

    print(f"Highs found at indices: {highs}")
    print(f"Lows found at indices: {lows}")

    df.loc[df.index, "extrema"] = "-"
    df.loc[highs, "extrema"] = 1
    df.loc[lows, "extrema"] = 0

    return

    # Find corresponding RSI values at those points
    results = []
    # Bullish divergence: price lower low, RSI higher low
    for i in range(1, len(lows)):
        prev, curr = lows[i - 1], lows[i]
        if (
            df["close"].iloc[curr] < df["close"].iloc[prev]
            and df["rsi"].iloc[curr] > df["rsi"].iloc[prev]
        ):
            results.append(
                {
                    "type": "bullish",
                    "index": curr,
                    "price": df["close"].iloc[curr],
                    "rsi": df["rsi"].iloc[curr],
                }
            )
    # Bearish divergence: price higher high, RSI lower high
    for i in range(1, len(highs)):
        prev, curr = highs[i - 1], highs[i]
        if (
            df["close"].iloc[curr] > df["close"].iloc[prev]
            and df["rsi"].iloc[curr] < df["rsi"].iloc[prev]
        ):
            results.append(
                {
                    "type": "bearish",
                    "index": curr,
                    "price": df["close"].iloc[curr],
                    "rsi": df["rsi"].iloc[curr],
                }
            )
    return results
