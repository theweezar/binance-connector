import util
import pandas
import indicator
import numpy as np


def process(frame: pandas.DataFrame):
    y_prices = frame["close"]

    frame["price_change"] = y_prices.pct_change()
    frame["volatility"] = y_prices.rolling(10).std()

    rsi_6 = indicator.calc_rsi(y_prices, 6)
    rsi_7 = indicator.calc_rsi(y_prices, 7)
    rsi_9 = indicator.calc_rsi(y_prices, 9)
    rsi_12 = indicator.calc_rsi(y_prices, 12)
    rsi_14 = indicator.calc_rsi(y_prices, 14)
    rsi_30 = indicator.calc_rsi(y_prices, 30)
    ema_34 = indicator.calc_ema(y_prices, 34)
    ema_89 = indicator.calc_ema(y_prices, 89)

    frame["rsi_6"] = rsi_6
    frame["rsi_7"] = rsi_7
    frame["rsi_9"] = rsi_9
    frame["rsi_12"] = rsi_12
    frame["rsi_14"] = rsi_14
    frame["rsi_30"] = rsi_30
    frame["ema_34"] = ema_34
    frame["ema_89"] = ema_89

    ema_trend = ema_34 - ema_89
    symbol = frame["symbol"][0]
    offsets = {
        "BTCUSDT": 75,
        "LTCUSDT": 1,
        "ETHUSDT": 10,
        "XRPUSDT": 0.1,
        "BNBUSDT": 1,
        "DOGEUSDT": 0.01,
        "PEPEUSDT": 0.01,
        "ADAUSDT": 0.01,
    }

    frame["ema_trend"] = ema_trend
    frame["ema_34_x_ema_89"] = (
        (ema_trend.abs() <= offsets[symbol]).astype(int).astype(str)
    )

    ema_12 = indicator.calc_ema(y_prices, 12)
    ema_26 = indicator.calc_ema(y_prices, 26)
    macd = ema_12 - ema_26

    frame["macd"] = macd
    frame["macd_signal"] = indicator.calc_ema(macd, 9)
    # frame.dropna(inplace=True)

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
        signal_dict["start"] = frame["start"][ema_x_last_index]
        signal_dict["end"] = frame["end"][ema_x_last_index]

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
    y_prices = frame["close"]
    symbol = frame["symbol"][0]
    period = 6
    offsets = {
        "BTCUSDT": 100,
        "LTCUSDT": 1,
        "ETHUSDT": 10,
        "XRPUSDT": 0.01,
        "BNBUSDT": 1,
        "DOGEUSDT": 0.01,
        "PEPEUSDT": 0.01,
        "ADAUSDT": 0.01,
    }
    offset = offsets[symbol]
    reach_level_list = [70, 75, 80, 90]
    reach_list = []
    drop_level_list = [30, 25, 20, 15]
    drop_list = []

    for level in reach_level_list:
        price_if_rsi_reach = indicator.calc_price_if_rsi_reach_to(
            y_prices, float(level), period, offset
        )
        this_dict = {"rsi": level, "priceIfRSIReach": price_if_rsi_reach}
        reach_list.append(this_dict)

    for level in drop_level_list:
        price_if_rsi_drop = indicator.calc_price_if_rsi_drop_to(
            y_prices, float(level), period, offset
        )
        this_dict = {"rsi": level, "priceIfRSIReach": price_if_rsi_drop}
        drop_list.append(this_dict)

    return {
        "period": period,
        "offset": offset,
        "reach_list": reach_list,
        "drop_list": drop_list,
    }


def update_api(frame: pandas.DataFrame) -> dict:
    lastest_data = {}
    last_idx = len(frame) - 1

    for prop in frame.keys():
        camelcase_prop = util.to_camelcase(prop)
        lastest_data[camelcase_prop] = frame[prop][last_idx]

    api_data = util.get_api()
    ema_signal_dict = detect_ema_signal(frame)
    rsi_signal_dict = detect_rsi_signal(frame)

    api_data["signal"] = {
        "ema34x89": ema_signal_dict,
        "futureRSI": {
            "period": rsi_signal_dict["period"],
            "offset": rsi_signal_dict["offset"],
            "reach": rsi_signal_dict["reach_list"],
            "drop": rsi_signal_dict["drop_list"],
        },
    }

    api_data["processor"] = lastest_data

    return api_data


if __name__ == "__main__":
    csv = util.get_csv()

    frame = process(csv["data_frame"])

    export_csv(csv["file_path"], frame)

    api = update_api(frame)

    util.save_api(api)
