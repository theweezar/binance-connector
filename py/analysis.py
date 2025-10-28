import fire
from util import file
import pandas as pd


def compare_price_with_line_series(
    df: pd.DataFrame, price_col: str, series_1_col: str, series_2_col: str
):
    """
    Compare price with two line series (e.g., EMA lines).
    Prints message if price is above/below both or between them.

    Args:
        df (pd.DataFrame): DataFrame containing the series.
        price_col (str): The column name of the price to compare.
        series_1_col (str): The column name of the first line series (e.g., ema_9).
        series_2_col (str): The column name of the second line series (e.g., ema_21).
    """
    last_row = df.iloc[-1]
    last_price = last_row[price_col]
    last_series_1 = last_row[series_1_col]
    last_series_2 = last_row[series_2_col]

    if last_price > last_series_1 and last_price > last_series_2:
        print(f"- Current price > {series_1_col} & {series_2_col}.")
    elif last_price < last_series_1 and last_price < last_series_2:
        print(f"- Current price < {series_1_col} & {series_2_col}.")
    elif (last_series_1 < last_price < last_series_2) or (
        last_series_2 < last_price < last_series_1
    ):
        print(f"- Current price is between series {series_1_col} & {series_2_col}.")


def check_line_series_cross(
    df: pd.DataFrame, series_1_col: str, series_2_col: str, window: int
):
    """
    Check if series_1 crosses series_2 up or down within the given window.
    Prints message if a cross is detected.

    Args:
        df (pd.DataFrame): DataFrame containing the series.
        series_1_col (str): The column name of the first line series (e.g., ema_9).
        series_2_col (str): The column name of the second line series (e.g., ema_21).
        window (int): Number of recent points to check.
    """
    ls1 = df[series_1_col][-window:].reset_index(drop=True)
    ls2 = df[series_2_col][-window:].reset_index(drop=True)
    for i in range(1, len(ls1)):
        prev_diff = ls1[i - 1] - ls2[i - 1]
        curr_diff = ls1[i] - ls2[i]
        if prev_diff < 0 and curr_diff > 0:
            print(f"- {series_1_col} has crossed up {series_2_col} within the last {window} candles.")
            break
        elif prev_diff > 0 and curr_diff < 0:
            print(f"- {series_1_col} has crossed down {series_2_col} within the last {window} candles.")
            break


def check_stoch_cross(
    df: pd.DataFrame, stoch_col: str, stoch_signal_col: str, window: int
):
    """
    Check if the stochastic oscillator crosses its signal line.
    Prints message if a cross is detected.

    Args:
        df (pd.DataFrame): DataFrame containing the stochastic oscillator and its signal.
        stoch_col (str): The column name of the stochastic oscillator (e.g., stoch_14).
        stoch_signal_col (str): The column name of the stochastic signal line (e.g., stoch_signal_14).
        window (int): Number of recent points to check.
    """

    ls1 = df[stoch_col][-window:].reset_index(drop=True)
    ls2 = df[stoch_signal_col][-window:].reset_index(drop=True)
    upper_bound = 80
    lower_bound = 20

    for i in range(1, len(ls1)):
        prev_stoch = ls1[i - 1]
        prev_stoch_signal = ls2[i - 1]
        curr_stoch = ls1[i]
        curr_stoch_signal = ls2[i]

        if (
            prev_stoch > lower_bound
            and prev_stoch_signal > lower_bound
            and curr_stoch > lower_bound
            and curr_stoch_signal > lower_bound
        ) and (
            prev_stoch < upper_bound
            and prev_stoch_signal < upper_bound
            and curr_stoch < upper_bound
            and curr_stoch_signal < upper_bound
        ):
            # Skipping cross detection if both values are within the middle range
            continue

        prev_diff = prev_stoch - prev_stoch_signal
        curr_diff = curr_stoch - curr_stoch_signal
        if prev_diff < 0 and curr_diff > 0:
            print(f"- Stochastic: %K has crossed up %D within the last {window} candles.")
            break
        elif prev_diff > 0 and curr_diff < 0:
            print(f"- Stochastic: %K has crossed down %D within the last {window} candles.")
            break


def compare_line_series(df: pd.DataFrame, series_1_col: str, series_2_col: str):
    """
    Compare two line series and print their relationship.
    Args:
        df (pd.DataFrame): DataFrame containing the series.
        series_1_col (str): The column name of the first line series (e.g., ema_9).
        series_2_col (str): The column name of the second line series (e.g., ema_21).
    """
    last_row = df.iloc[-1]
    last_series_1 = last_row[series_1_col]
    last_series_2 = last_row[series_2_col]

    if last_series_1 > last_series_2:
        print(f"- {series_1_col} > {series_2_col}.")
    elif last_series_1 < last_series_2:
        print(f"- {series_1_col} < {series_2_col}.")
    else:
        print(f"- {series_1_col} = {series_2_col}.")


def print_rsi(df: pd.DataFrame, rsi_col: str):
    """
    Print RSI values and their relationship to thresholds.

    Args:
        df (pd.DataFrame): DataFrame containing the RSI column.
        rsi_col (str): The column name of the RSI series.
    """
    last_rsi = df[rsi_col].iloc[-1]
    print(f"- Current {rsi_col} = {int(last_rsi)}.")


def has_engulfing(df, window):
    """
    Detect bullish or bearish engulfing pattern within the last `window` candles.
    Prints message if found.

    Args:
        df (pd.DataFrame): DataFrame with 'open' and 'close' columns.
        window (int): Number of recent candles to check.
    """
    for i in range(-window, 0):
        if i - 1 < -len(df):
            continue
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        # Bullish engulfing
        if (
            prev["close"] < prev["open"]
            and curr["close"] > curr["open"]
            and curr["close"] > prev["open"]
            and curr["open"] < prev["close"]
        ):
            print(
                f"- Bullish engulfing candle appeared within the last {window} candles."
            )
        # Bearish engulfing
        if (
            prev["close"] > prev["open"]
            and curr["close"] < curr["open"]
            and curr["open"] > prev["close"]
            and curr["close"] < prev["open"]
        ):
            print(
                f"- Bearish engulfing candle appeared within the last {window} candles."
            )


def has_shooting_star(df, window):
    """
    Detect shooting star pattern within the last `window` candles.
    Prints message if found.

    Args:
        df (pd.DataFrame): DataFrame with 'open', 'close', 'high', 'low' columns.
        window (int): Number of recent candles to check.
    """
    for i in range(-window, 0):
        row = df.iloc[i]
        body = abs(row["close"] - row["open"])
        upper_shadow = row["high"] - max(row["close"], row["open"])
        lower_shadow = min(row["close"], row["open"]) - row["low"]
        if (
            body < (row["high"] - row["low"]) * 0.3
            and upper_shadow > body * 2
            and lower_shadow < body
        ):
            print(f"- Shooting star candle appeared within the last {window} candles.")


def has_hammer(df, window):
    """
    Detect hammer pattern within the last `window` candles.
    Prints message if found.

    Args:
        df (pd.DataFrame): DataFrame with 'open', 'close', 'high', 'low' columns.
        window (int): Number of recent candles to check.
    """
    for i in range(-window, 0):
        row = df.iloc[i]
        body = abs(row["close"] - row["open"])
        upper_shadow = row["high"] - max(row["close"], row["open"])
        lower_shadow = min(row["close"], row["open"]) - row["low"]

        if body == 0:
            body = 0.001

        if (
            body
            < (row["high"] - row["low"])
            * 0.3  # Body is less than 30% of the total range
            and lower_shadow >= body * 2
            and upper_shadow <= 0.2 * body
        ):
            print(f"- Hammer candle appeared within the last {window} candles.")

        if (
            body
            < (row["high"] - row["low"])
            * 0.3  # Body is less than 30% of the total range
            and lower_shadow <= 0.2 * body
            and upper_shadow >= 2 * body
        ):
            print(
                f"- Inverted Hammer candle appeared within the last {window} candles."
            )


def has_doji(df, window):
    """
    Detect doji pattern within the last `window` candles.
    Prints message if found.

    Args:
        df (pd.DataFrame): DataFrame with 'open', 'close', 'high', 'low' columns.
        window (int): Number of recent candles to check.
    """
    count = 0
    for i in range(-window, 0):
        row = df.iloc[i]
        body = abs(row["close"] - row["open"])
        total_range = row["high"] - row["low"]
        if total_range == 0:
            continue
        if body / total_range < 0.15:  # Body is less than 15% of the total range
            count += 1

    if count > 0:
        print(f"- {count} Doji candle appeared within the last {window} candles.")


class Analysis(object):
    def analyze(self, source, interval):
        """
        Train a model using the provided module and source data.

        Args:
            source (str): The path to the source data.
            interval (str): The time interval for the analysis (e.g., '1m', '5m').
        """
        df = file.get_source(source)

        print(f"\nIn chart {interval}:")

        check_line_series_cross(df, "ema_9", "ema_21", window=6)

        compare_price_with_line_series(df, "close", "ema_9", "ema_21")

        compare_line_series(df, "ema_9", "ema_21")

        print_rsi(df, "rsi_9")

        check_stoch_cross(df, "stoch_5", "stoch_signal_5", window=6)

        has_engulfing(df, window=3)

        # has_shooting_star(df, window=3)

        has_hammer(df, window=3)

        has_doji(df, window=3)


if __name__ == "__main__":
    analysis = Analysis()
    fire.Fire(analysis)
