import util
import pandas
import indicator
import numpy as np


def process(frame: pandas.DataFrame):
    y_prices = frame["Close"]

    y_prices_nd_array = np.array(frame["Close"])

    rsi_7 = indicator.calc_rsi(y_prices, 7)

    rsi_14 = indicator.calc_rsi(y_prices, 14)

    rsi_30 = indicator.calc_rsi(y_prices, 30)

    ema_34 = indicator.calc_ema(y_prices_nd_array, 34)

    ema_89 = indicator.calc_ema(y_prices_nd_array, 89)

    frame["rsi_7"] = rsi_7

    frame["rsi_14"] = rsi_14

    frame["rsi_30"] = rsi_30

    frame["ema_34"] = ema_34

    frame["ema_89"] = ema_89

    ema_34_x_ema_89 = (ema_34 - ema_89).abs()

    # TODO: ema_34 crosses ema_89 is incorrect. Need to investigate and fix
    frame["ema_34_x_ema_89"] = (ema_34_x_ema_89 <= 75).astype(int).astype(str)

    return frame


def export_csv(path: str, frame: pandas.DataFrame):
    with open(path, "w") as csv_file:
        csv_file.write(frame.to_csv())


def detect_ema_signal(frame: pandas.DataFrame):
    ema_34_x_ema_89 = frame["ema_34_x_ema_89"].to_list()
    ema_x_last_index = -1
    signal_dict = {}

    try:
        ema_x_last_index = "".join(ema_34_x_ema_89).rindex("1")
    except:
        ema_x_last_index = -1

    if ema_x_last_index != -1:
        signal_dict["lastIndex"] = ema_x_last_index
        signal_dict["openTime"] = frame["Open Time"][ema_x_last_index]
        signal_dict["closeTime"] = frame["Close Time"][ema_x_last_index]

        ema_34 = frame["ema_34"][ema_x_last_index]
        ema_89 = frame["ema_89"][ema_x_last_index]

        signal_dict["ema34"] = ema_34
        signal_dict["ema89"] = ema_89

        if ema_x_last_index > 0:
            prev_ema_34 = frame["ema_34"][ema_x_last_index - 1]
            prev_ema_89 = frame["ema_89"][ema_x_last_index - 1]
            signal_dict["direction"] = "Up" if prev_ema_34 <= prev_ema_89 else "Down"
        else:
            signal_dict["direction"] = "Up" if ema_34 <= ema_89 else "Down"

    return signal_dict


def update_existing_api(frame: pandas.DataFrame) -> dict:
    lastest_data = {}
    last_idx = len(frame) - 1

    for prop in frame.keys():
        camelcase_prop = util.to_camelcase(prop)
        lastest_data[camelcase_prop] = frame[prop][last_idx]

    api_data = util.get_api()
    ema_signal_dict = detect_ema_signal(frame)

    api_data["signal"] = {}
    api_data["signal"]["ema34XEma89"] = ema_signal_dict
    api_data["processor"] = lastest_data

    return api_data


if __name__ == "__main__":
    csv = util.get_csv()

    frame = process(csv["data_frame"])

    export_csv(csv["file_path"], frame)

    util.save_api(update_existing_api(frame))
