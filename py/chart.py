import matplotlib
import matplotlib.axes
import numpy as np
import pandas
import indicator

class Chart:
    def __init__(self, plt: matplotlib.axes.Axes):
        self.plt = plt
        self.initial_nd_array = np.array([])
        self.current_nd_array = np.array([])
        self.x_nd_timestamps = np.array(range(len([])))

    def set_initial_nd_array(self, input_nd_array: np.ndarray):
        self.initial_nd_array = input_nd_array
        self.current_nd_array = input_nd_array
        self.x_nd_timestamps = np.array(range(len(input_nd_array)))
        return self

    def show_trendline(self):
        m, b = np.polyfit(self.x_nd_timestamps, self.current_nd_array, 1)
        trendline = m * self.x_nd_timestamps + b
        self.plt.plot(self.x_nd_timestamps, trendline, color="red", linestyle="--")
        current_xlabel = self.plt.get_xlabel()
        trend = "Neutral"

        if m > 0:
            trend = "Up"
        elif m < 0:
            trend = "Down"
        
        self.plt.set_xlabel(f"{current_xlabel} | Trend: {trend}")

        return self

    def show_chart(self, xlabel="Last", ylabel="Price"):
        self.plt.plot(self.x_nd_timestamps, self.initial_nd_array, color="black")
        self.plt.set_xlabel(f"{xlabel}: {self.initial_nd_array[-1]}")
        self.plt.set_ylabel(ylabel)
        self.plt.grid(linestyle='--')
        return self

    def show_rsi(self, period: int):
        price_count = len(self.initial_nd_array)
        upper = np.full(price_count, 80 if period < 10 else 70)
        lower = np.full(price_count, 20 if period < 10 else 30)
        price_series = pandas.Series(self.initial_nd_array)
        rsi_series = indicator.calc_rsi(price_series, period)
        rsi_nd_array = np.array(rsi_series)
        y_ticks = [i*10 for i in range(11)]

        self.plt.plot(self.x_nd_timestamps, rsi_nd_array, color="black")
        self.plt.plot(self.x_nd_timestamps, upper, color="green")
        self.plt.plot(self.x_nd_timestamps, lower, color="green")
        self.plt.set_xlabel(f"RSI({period}): {round(rsi_nd_array[-1], 2)}")
        self.plt.set_ylabel("RSI")
        self.plt.set_ylim(ymin=0, ymax=100)
        self.plt.grid(linestyle='--')
        self.plt.set_yticks(y_ticks)

        self.current_nd_array = rsi_nd_array

        return self
    
    def show_ema(self, period: int, color: str):
        ema_series = indicator.calc_ema(self.initial_nd_array, period)
        ema_nd_array = np.array(ema_series)

        self.plt.plot(self.x_nd_timestamps, ema_nd_array, color=color)

        return self
    
    def set_text(self, text: str):
        self.plt.set_xticks([])
        self.plt.set_yticks([])
        self.plt.axis('off')
        self.plt.text(0, 0.8, text)

        return self
        