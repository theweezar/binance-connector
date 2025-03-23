import util
import numpy as np
from view import View
from matplotlib.pylab import figtext

# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html

# Initial price data
csv = util.get_csv()
csv_file_name = csv["file_name"]
frame = csv["data_frame"]
symbol = frame["symbol"][0]
open_time = frame["start"][0]
close_time = frame["end"]
close_time = close_time[len(close_time) - 1]
y_prices = np.array(frame["close"])
y_vols = np.array(frame["vol"])

# Plot 2 charts, plot the prices and the trendline
view = View(3, y_prices)

view.get_chart(0).show_chart(
    xlabel=f'{symbol} From "{open_time}" to "{close_time}"'
).show_trendline().show_ema(34, "green").show_ema(89, "blue")

view.get_chart(1).show_rsi(7).show_trendline()

# view.get_chart(2).set_initial_nd_array(y_vols).show_chart(xlabel="VOL Last", ylabel="VOL").show_trendline()

view.get_chart(2).set_text(
    f"""
    - file: {csv_file_name}
    - symbol: {symbol}
    - open time (GMT): {open_time}
    - close time (GMT): {close_time}
    - count: 500
    - ema(34): green
    - ema(89): blue
    """
)

view.export()

# view.show()
