import ta.momentum
import ta.trend
import util
import pandas
import indicator
import numpy as np
import ta


def process(frame: pandas.DataFrame):
    close = frame["close"]
    high = frame["high"]
    low = frame["low"]

    frame["price_change"] = close.pct_change()
    frame["volatility"] = close.rolling(10).std()

    rsi_6 = ta.momentum.rsi(close, 6)
    rsi_7 = ta.momentum.rsi(close, 7)
    rsi_9 = ta.momentum.rsi(close, 9)
    rsi_12 = ta.momentum.rsi(close, 12)
    rsi_14 = ta.momentum.rsi(close, 14)
    rsi_30 = ta.momentum.rsi(close, 30)
    ema_34 = ta.trend.ema_indicator(close, 34)
    ema_89 = ta.trend.ema_indicator(close, 89)

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

    ema_12 = ta.trend.ema_indicator(close, 12)
    ema_26 = ta.trend.ema_indicator(close, 26)
    macd = ema_12 - ema_26

    frame["macd"] = macd
    frame["macd_signal"] = ta.trend.ema_indicator(macd, 9)

    frame["adx_14"] = ta.trend.ADXIndicator(high, low, close).adx()

    return frame


def export_csv(path: str, frame: pandas.DataFrame):
    with open(path, "w") as csv_file:
        csv_file.write(frame.to_csv(index_label="index"))


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
    drop_level_list = [30, 25, 20, 10]
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
    # ema_signal_dict = detect_ema_signal(frame)
    # rsi_signal_dict = detect_rsi_signal(frame)

    # api_data["signal"] = {
    #     "ema34x89": ema_signal_dict,
    #     "futureRSI": {
    #         "period": rsi_signal_dict["period"],
    #         "offset": rsi_signal_dict["offset"],
    #         "reach": rsi_signal_dict["reach_list"],
    #         "drop": rsi_signal_dict["drop_list"],
    #     },
    # }

    api_data["processor"] = lastest_data

    return api_data


if __name__ == "__main__":
    csv = util.get_csv()

    frame = process(csv["data_frame"])

    export_csv(csv["file_path"], frame)

    api = update_api(frame)

    util.save_api(api)
