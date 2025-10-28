import csv
import time
import requests
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from fire import Fire


def fetch(symbol: str, interval: str, limit: int = 500, endTime: int = None) -> dict:
    """
    Fetch Kline/Candlestick data from BingX API.
    Parameters:
    - symbol (str): Trading pair symbol (e.g., "XAUT-USDT").
    - interval (str): Time interval for each candlestick (e.g., "1m", "5m", "1h", "1d").
    - limit (int): Number of candlesticks to retrieve (default is 500, max is 500).
    - endTime (int): End time in milliseconds since epoch (optional).
    Returns:
    - dict: Parsed JSON response from the API containing candlestick data.

    """
    APIURL = "https://open-api.bingx.com"
    paramsMap = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    if endTime is not None:
        paramsMap["endTime"] = endTime
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    if paramsStr != "":
        paramsStr += "&timestamp=" + str(int(time.time() * 1000))
    else:
        paramsStr = "timestamp=" + str(int(time.time() * 1000))

    # Make request
    path = "/openApi/swap/v3/quote/klines"
    url = "%s%s?%s" % (APIURL, path, paramsStr)
    response = requests.get(url)

    return json.loads(response.text)


INTERVAL_MS_MAP = {
    "1m": 60 * 1000,
    "3m": 3 * 60 * 1000,
    "5m": 5 * 60 * 1000,
    "15m": 15 * 60 * 1000,
    "30m": 30 * 60 * 1000,
    "1h": 60 * 60 * 1000,
    "2h": 2 * 60 * 60 * 1000,
    "4h": 4 * 60 * 60 * 1000,
    "6h": 6 * 60 * 60 * 1000,
    "8h": 8 * 60 * 60 * 1000,
    "12h": 12 * 60 * 60 * 1000,
    "1d": 24 * 60 * 60 * 1000,
    "3d": 3 * 24 * 60 * 60 * 1000,
    "1w": 7 * 24 * 60 * 60 * 1000,
    "1M": 30 * 24 * 60 * 60 * 1000,
}


class KlineCollection:
    def __init__(self, symbol: str, interval: str, raw_data, connector_type: str):
        self.symbol = symbol
        self.interval = interval
        self.raw_data = raw_data
        self.connector_type = connector_type
        pass


class Connector(ABC):

    def __init__(self):
        self.max_limit = 500

    @abstractmethod
    def fetch_by_chunk(self, symbol: str, interval: str, chunk: int):
        pass


class BingXConnector(Connector):
    def fetch_by_chunk(self, symbol: str, interval: str, chunk: int) -> KlineCollection:
        limit = self.max_limit
        all_klines = []
        end_time = int(datetime.now().timestamp() * 1000)
        print(
            f"Fetching {chunk} chunk(s) of {limit} candles each (up to {chunk * limit} candles)..."
        )
        for i in range(chunk):
            result = fetch(
                symbol=symbol, interval=interval, limit=limit, endTime=end_time
            )
            klines = result["data"]
            if type(klines) is not list or len(klines) == 0:
                break
            klines.reverse()

            if i > 0:
                klines = klines[0 : len(klines) - 1]

            all_klines = klines + all_klines
            end_time = klines[0]["time"] - 1

        return KlineCollection(symbol, interval, all_klines, "bingx")


class ConnectorAdapter:
    def __init__(self, kline_collection: KlineCollection):
        self.kline_collection = kline_collection

    def _normalize_data(self):
        if self.kline_collection.connector_type == "bingx":
            return self._normalize_bingx_data()
        else:
            raise ValueError("Unsupported connector type")

    def _normalize_bingx_data(self):
        normalized = []
        for candle in self.kline_collection.raw_data:
            timestamp = candle["time"]
            open_time = datetime.fromtimestamp(timestamp / 1000)
            end_time = open_time + timedelta(
                milliseconds=INTERVAL_MS_MAP[self.kline_collection.interval]
            )
            normalized.append(
                {
                    "symbol": self.kline_collection.symbol,
                    "timestamp": open_time.timestamp(),
                    "date": open_time.strftime("%Y-%m-%d"),
                    "start": open_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": float(candle["open"]),
                    "high": float(candle["high"]),
                    "low": float(candle["low"]),
                    "close": float(candle["close"]),
                    "volume": float(candle["volume"]),
                }
            )
        return normalized


def write_csv(filename: str, data: list):
    if not data or len(data) == 0:
        print("No data to write.")
        return

    keys = data[0].keys()
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# python bingx.py run --symbol=XAUT-USDT --interval=1m --output=ignore/XAUT-USDT_1m.csv --chunk=1
class BingX_CLI:
    def __init__(self, symbol: str, interval: str, output: str, chunk: int = 1):
        self.symbol = symbol
        self.interval = interval
        self.output = output
        self.chunk = chunk

    def run(self):
        # Create BingX instance and execute fetch
        bingx = BingXConnector()
        data = bingx.fetch_by_chunk(
            symbol=self.symbol, interval=self.interval, chunk=self.chunk
        )
        adapter = ConnectorAdapter(data)
        normalized_data = adapter._normalize_data()
        write_csv(self.output, normalized_data)
        print(f"Data saved to {self.output}")


if __name__ == "__main__":
    Fire(BingX_CLI)
