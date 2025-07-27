import fire
import pandas as pd
import matplotlib.pyplot as plt
from util import file
from datetime import datetime, timezone


def select_short_position_maximum_of(
    df: pd.DataFrame, column_name: str, steps: int = 5
):
    """
    For each rolling window of 'steps', keep only the short position (position==0)
    with the maximum value in the specified column, set others to "-".

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_name (str): Column to find the maximum value for short positions.
        steps (int): Size of the rolling window.

    Returns:
        pd.DataFrame: DataFrame with only the maximum short position kept per window.
    """
    cp_df = df.copy()

    for i in range(0, len(cp_df) - steps + 1):
        # Select group by steps
        group_by_steps = cp_df[i : i + steps]
        # Select short positions in group
        group_has_short = group_by_steps[group_by_steps["position"] == 0]

        if group_has_short.empty:
            continue

        max_value = group_has_short[column_name].max()
        max_index = group_has_short[group_has_short[column_name] == max_value].index[0]
        cp_df.loc[group_has_short.index, "position"] = "-"
        cp_df.loc[max_index, "position"] = 0
        # print(f"Found maximum {max_value} at index {max_index} for short position")

    return cp_df


def select_long_position_minimum_of(df: pd.DataFrame, column_name: str, steps: int = 5):
    """
    For each rolling window of 'steps', keep only the long position (position==1)
    with the minimum value in the specified column, set others to "-".

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_name (str): Column to find the minimum value for long positions.
        steps (int): Size of the rolling window.

    Returns:
        pd.DataFrame: DataFrame with only the minimum long position kept per window.
    """
    cp_df = df.copy()

    for i in range(0, len(cp_df) - steps + 1):
        # Select group by steps
        group_by_steps = cp_df[i : i + steps]
        # Select long positions in group
        group_has_long = group_by_steps[group_by_steps["position"] == 1]

        if group_has_long.empty:
            continue

        min_value = group_has_long[column_name].min()
        min_index = group_has_long[group_has_long[column_name] == min_value].index[0]
        cp_df.loc[group_has_long.index, "position"] = "-"
        cp_df.loc[min_index, "position"] = 1
        # print(f"Found minimum {min_value} at index {min_index} for long position")

    return cp_df


def start_plot(plot_df: pd.DataFrame):
    """
    Plot the last N rows with markers for positions.

    Args:
        plot_df (pd.DataFrame): DataFrame to plot.
    """
    plt.figure(figsize=(16, 8))
    plt.plot(plot_df["close"], label="Close Price", color="blue")

    # Plot markers for positions (dot marker, color as before)
    for idx, row in plot_df.iterrows():
        if row["position"] == 1:
            plt.scatter(
                idx,
                row["close"],
                color="green",
                marker="o",
                s=80,
                label="Long" if idx == 0 else "",
            )
        elif row["position"] == 0:
            plt.scatter(
                idx,
                row["close"],
                color="red",
                marker="o",
                s=80,
                label="Short" if idx == 0 else "",
            )

    plt.title(f"Backtest Plot (Last {len(plot_df)} rows)")
    plt.xlabel("Index")
    plt.ylabel("Close Price")
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.tight_layout()
    plt.show()


def apply_long(df: pd.DataFrame):
    long_mask = df["rsi_6_low"] < 20
    # long_mask = long_mask & (df["close"] > df["ema_34"])
    # long_mask = long_mask & (df["close"] > df["donchian_high"].shift(1))
    # long_mask = long_mask & (df["adx"] > 25) & (df["+di"] > df["-di"])
    df.loc[long_mask, "position"] = 1
    return df


def apply_short(df: pd.DataFrame):
    short_mask = df["rsi_6_high"] > 80
    # short_mask = short_mask & (df["close"] < df["ema_34"])
    # short_mask = short_mask & (df["close"] < df["donchian_low"].shift(1))
    # short_mask = short_mask & (df["adx"] > 25) & (df["-di"] > df["+di"])
    df.loc[short_mask, "position"] = 0
    return df


def is_bullish_engulfing(row, prev_row):
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


def is_bearish_engulfing(row, prev_row):
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


def signal_generator(df):
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
        bullish_cross = (
            prev["ema_9"] < prev["ema_21"] and curr["ema_9"] > curr["ema_21"]
        )
        bearish_cross = (
            prev["ema_9"] > prev["ema_21"] and curr["ema_9"] < curr["ema_21"]
        )
        bullish_engulf = is_bullish_engulfing(curr, prev)
        bearish_engulf = is_bearish_engulfing(curr, prev)
        rsi_ok_long = curr["rsi_14"] > 50
        rsi_ok_short = curr["rsi_14"] < 50
        # Long entry conditions
        if bullish_cross and bullish_engulf and rsi_ok_long:
            df.at[df.index[i], "position"] = 1
        # Short entry conditions
        if bearish_cross and bearish_engulf and rsi_ok_short:
            df.at[df.index[i], "position"] = 0
    return df


class Back_Test_CLI:
    """
    CLI tool for simple backtesting and plotting based on RSI signals.
    """

    def compute(
        self,
        source: str,
        plot: str = None,
        output: str = None,
        tail: int = 1000,
        filter: str = None,
    ):
        """
        Perform backtest, export, and plot results.

        Args:
            source (str): Path to the CSV file containing the data.
            plot (str): If "true", plot the last N rows.
            output (str): Path to export the last 1000 rows as CSV.
            tail (int): Number of rows to plot from the end of the DataFrame.
            filter (str): Filter to apply on the DataFrame.
        """
        # Load data
        src = file.get_source(source)
        df = src["dataframe"]

        # Set position column based on RSI conditions
        df["position"] = "-"

        # Long condition
        df = apply_long(df)

        # Short condition
        df = apply_short(df)

        # Signal generator
        df = signal_generator(df)

        # Plot last N rows
        plot_df = df.tail(tail).reset_index(drop=True)
        count_position = df[df["position"] != "-"]

        print(f"Found {len(count_position)} positions in the last {tail} rows.")

        # TODO: Write a function to combine RSI and ADX to generate signal.
        # TODO: Write a function to calculate profit/loss based on positions.

        if filter == "select-max-min":
            plot_df = select_short_position_maximum_of(plot_df, "rsi_6_high", steps=6)
            plot_df = select_long_position_minimum_of(plot_df, "rsi_6_low", steps=6)

        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.strftime("%Y-%m-%d")
        count_position_today = count_position[count_position["date"] == now_str]
        print(f"Found {len(count_position_today)} positions today.")

        if output:
            file.write_dataframe(plot_df, output)
            print(
                f"Successfully processed backtest for {source}. Exported last {tail} rows"
            )

        if plot == "true":
            start_plot(plot_df)


if __name__ == "__main__":
    fire.Fire(Back_Test_CLI)
