import util
import indicator
import numpy as np

csv = util.get_csv()

frame = csv["data_frame"]

y_prices = frame['Close']

y_prices_nd_array = np.array(frame['Close'])

rsi_7 = indicator.calc_rsi(y_prices, 7)

rsi_14 = indicator.calc_rsi(y_prices, 14)

rsi_30 = indicator.calc_rsi(y_prices, 30)

ema_34 = indicator.calc_ema(y_prices_nd_array, 34)

ema_89 = indicator.calc_ema(y_prices_nd_array, 89)

frame['rsi_7'] = rsi_7

frame['rsi_14'] = rsi_14

frame['rsi_30'] = rsi_30

frame['ema_34'] = ema_34

frame['ema_89'] = ema_89

with open(csv["file_path"], "w") as csv_file:
    csv_file.write(frame.to_csv())