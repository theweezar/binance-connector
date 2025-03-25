import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import util


class Backtest:
    def __init__(self, data: pd.DataFrame, symbol: str, interval: str):
        self.frame = data
        self.symbol = symbol
        self.interval = interval

    def extract_latest_rows(self, count: int):
        frame = self.frame.copy()
        fsize = len(frame)
        frame = frame[fsize - count : fsize]
        frame["index"] = np.array(range(len(frame)))

        self.frame = frame

    def generate_signals(self):
        frame = self.frame.copy()
        frame["signal"] = 0

        sell_conds = [frame["rsi_6"] >= 80, frame["rsi_9"] >= 70]
        buy_conds = [frame["rsi_6"] <= 20, frame["rsi_9"] <= 30]

        frame.loc[np.bitwise_and.reduce(sell_conds), "signal"] = -1  # sell
        frame.loc[np.bitwise_and.reduce(buy_conds), "signal"] = 1  # buy

        self.frame = frame

    def plot_trade_signals(self):
        buy_signals = self.frame[self.frame["signal"] == 1]
        sell_signals = self.frame[self.frame["signal"] == -1]

        print(f"Buy signal count: {len(buy_signals)}")
        print(f"Sell signal count: {len(sell_signals)}")

        plt.figure(figsize=(12, 6))
        plt.plot(
            self.frame["index"], self.frame["close"], label="Close Price", alpha=0.5,
        )
        plt.scatter(
            buy_signals["index"],
            buy_signals["close"],
            color="green",
            marker="^",
            label="Buy Signal"
        )
        plt.scatter(
            sell_signals["index"],
            sell_signals["close"],
            color="red",
            marker="v",
            label="Sell Signal"
        )
        plt.legend()
        plt.title(f"{self.symbol} {self.interval} - Timestamp: {len(self.frame)}")
        plt.ylabel("Price")
        plt.show()


# Example Usage:
if __name__ == "__main__":
    csv = util.get_csv()
    frame = csv["data_frame"]

    api = util.get_api()
    symbol = api["symbol"]
    interval = api["interval"]

    backtest = Backtest(frame, symbol, interval)
    backtest.extract_latest_rows(50)
    backtest.generate_signals()
    backtest.plot_trade_signals()
