import fire
import pandas as pd
import matplotlib.pyplot as plt
from util import file


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


class Back_Test_CLI:
    """
    CLI tool for simple backtesting and plotting based on RSI signals.
    """

    def compute(
        self, source: str, plot: str = None, output: str = None, tail: int = 1000
    ):
        """
        Perform backtest, export, and plot results.

        Args:
            source (str): Path to the CSV file containing the data.
            plot (str): If "true", plot the last N rows.
            output (str): Path to export the last 1000 rows as CSV.
            tail (int): Number of rows to plot from the end of the DataFrame.
        """
        # Load data
        src = file.get_source(source)
        df = src["dataframe"]

        # Set position column based on RSI conditions
        df["position"] = "-"

        # Long condition: rsi_6_of_low < 27 and rsi_9_of_low < 30
        long_mask = (df["rsi_6_of_low"] < 27) #& (df["rsi_9_of_low"] < 30)
        df.loc[long_mask, "position"] = 1  # Long

        # Short condition: rsi_6_of_high > 90 and rsi_9_of_high > 89
        short_mask = (df["rsi_6_of_high"] > 90) #& (df["rsi_9_of_high"] > 89)
        df.loc[short_mask, "position"] = 0  # Short

        # Plot last N rows
        plot_df = df.tail(tail).reset_index(drop=True)
        count_position = df[df["position"] != "-"]

        print(f"Found {len(count_position)} positions in the last {tail} rows.")

        # TODO: Write a function to calculate profit/loss based on positions.

        # TODO: Write a function to calculate the highest RSI(6) when position is short(0) and there are multiple stand next to each other.
        plot_df = select_short_position_maximum_of(plot_df, "rsi_6_of_high", steps=6)
        # TODO: Write a function to calculate the lowest RSI(6) when position is long(1) and there are multiple stand next to each other.
        plot_df = select_long_position_minimum_of(plot_df, "rsi_6_of_low", steps=6)

        if output:
            resolved_output = file.resolve(output)
            with open(resolved_output, "w") as f:
                f.write(plot_df.to_csv(index_label="index", lineterminator="\n"))
                print(f"Exported last {tail} rows to {resolved_output}")

        if plot == "true":
            start_plot(plot_df)


if __name__ == "__main__":
    fire.Fire(Back_Test_CLI)
