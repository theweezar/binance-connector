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


def detect_rsi_signal(frame: pandas.DataFrame):
    y_prices = frame["Close"]

    period = 14
    offset = 100

    reach_list = [70, 75, 80, 90]
    reach_list_dict = []

    drop_list = [30, 25, 20, 15]
    drop_list_dict = []

    for i in range(len(reach_list)):
        price_if_rsi_reach = indicator.calc_price_if_rsi_reach_to(
            y_prices, float(reach_list[i]), period, offset
        )
        this_dict = {"rsi": reach_list[i], "priceIfRSIReach": price_if_rsi_reach}
        reach_list_dict.append(this_dict)

    for i in range(len(drop_list)):
        price_if_rsi_drop = indicator.calc_price_if_rsi_drop_to(
            y_prices, float(drop_list[i]), period, offset
        )
        this_dict = {"rsi": drop_list[i], "priceIfRSIReach": price_if_rsi_drop}
        drop_list_dict.append(this_dict)

    return {
        "period": period,
        "offset": offset,
        "reach_list_dict": reach_list_dict,
        "drop_list_dict": drop_list_dict,
    }


def update_existing_api(frame: pandas.DataFrame) -> dict:
    lastest_data = {}
    last_idx = len(frame) - 1

    for prop in frame.keys():
        camelcase_prop = util.to_camelcase(prop)
        lastest_data[camelcase_prop] = frame[prop][last_idx]

    api_data = util.get_api()
    ema_signal_dict = detect_ema_signal(frame)
    rsi_signal_dict = detect_rsi_signal(frame)

    api_data["signal"] = {
        "ema34XEma89": ema_signal_dict,
        "futureRSI": {
            "period": rsi_signal_dict["period"],
            "offset": rsi_signal_dict["offset"],
            "reach": rsi_signal_dict["reach_list_dict"],
            "drop": rsi_signal_dict["drop_list_dict"],
        },
    }

    api_data["processor"] = lastest_data

    return api_data


if __name__ == "__main__":
    csv = util.get_csv()

    frame = process(csv["data_frame"])

    export_csv(csv["file_path"], frame)

    util.save_api(update_existing_api(frame))
