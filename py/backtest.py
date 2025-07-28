import fire
import pandas as pd
import matplotlib.pyplot as plt
from util import file, strategy
from datetime import datetime, timezone


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
        df = file.get_source(source)

        # Plot last N rows
        plot_df = df.tail(tail).reset_index(drop=True)

        # Set position column based on RSI conditions
        plot_df["position"] = "-"
        plot_df["sensitive_position"] = "-"
        plot_df = strategy.apply_rsi_6(plot_df)
        count_position = plot_df[plot_df["position"] != "-"]

        print(f"Found {len(count_position)} positions in the last {tail} rows.")

        if filter == "select-max-min":
            plot_df = strategy.select_short_position_maximum_of(
                plot_df, "rsi_6_high", steps=6
            )
            plot_df = strategy.select_long_position_minimum_of(
                plot_df, "rsi_6_low", steps=6
            )

        # plot_df = strategy.apply_rsi_adx_trends(plot_df)

        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.strftime("%Y-%m-%d")
        count_position_today = count_position[count_position["date"] == now_str]
        print(f"Found {len(count_position_today)} positions today in UTC timezone.")

        if output:
            file.write_dataframe(plot_df, output)
            print(
                f"Successfully processed backtest for {source}. Exported last {tail} rows"
            )

        if plot == "true":
            start_plot(plot_df)


if __name__ == "__main__":
    fire.Fire(Back_Test_CLI)
