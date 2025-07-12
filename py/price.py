import csv
import datetime
import os
import fire
import csv
import datetime
from util import file
from binance.spot import Spot


class Price_CLI:
    """
    CLI tool to fetch Kline/Candlestick data from Binance and export to CSV.

    Example usage:
        python price.py fetch --symbol=BTCUSDT --interval=1d --path=ignore/btc.csv --chunk=3
        python price.py fetch --symbol=BTCUSDT --interval=1d --path=ignore/btc.csv --from_=2023-01-01 --to=2025-07-12
    """

    def fetch(
        self,
        symbol: str,
        interval: str = "1d",
        path: str = "output.csv",
        chunk: int = None,
        from_: str = None,
        to: str = None,
    ):
        """
        Fetch Kline/Candlestick data from Binance and export to CSV.

        Args:
            symbol (str): Symbol to fetch, e.g. BTCUSDT
            interval (str): Interval, e.g. 1d, 1h, 15m
            path (str): Output CSV file path
            chunk (int): Number of chunks to fetch. Each chunk fetches up to 500 candles (Binance API limit).
                The higher the chunk, the more historical data is fetched and the longer the process takes.
            from_ (str): Start date (YYYY-MM-DD), required if chunk is not provided.
            to (str): End date (YYYY-MM-DD), required if chunk is not provided.
        """
        client = Spot()
        limit = 500
        all_klines = []

        # If chunk is provided, prioritize chunk logic
        if chunk is not None:
            end_time = int(datetime.datetime.now().timestamp() * 1000)
            print(
                f"Fetching {chunk} chunk(s) of {limit} candles each (up to {chunk * limit} candles)..."
            )
            for i in range(chunk):
                klines = client.klines(
                    symbol=symbol, interval=interval, limit=limit, endTime=end_time
                )
                if not klines:
                    break
                all_klines = klines + all_klines
                end_time = klines[0][0] - 1
        else:
            # Validate from_ and to
            if not from_ or not to:
                raise ValueError(
                    'Both "from_" and "to" arguments are required when "chunk" is not provided.'
                )
            try:
                from_dt = datetime.datetime.strptime(from_, "%Y-%m-%d")
                to_dt = datetime.datetime.strptime(to, "%Y-%m-%d")
            except Exception:
                raise ValueError(
                    'Arguments "from_" and "to" must be in format YYYY-MM-DD.'
                )
            if from_dt > to_dt:
                raise ValueError('"from_" date must be before or equal to "to" date.')

            start_time = int(
                from_dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
            )
            end_time = int(
                to_dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
            )
            total_ms = end_time - start_time
            # Estimate average candle ms for interval
            interval_map = {
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
            candle_ms = interval_map.get(interval, 24 * 60 * 60 * 1000)
            est_candles = total_ms // candle_ms + 1
            est_chunks = (est_candles + limit - 1) // limit
            print(
                f"Fetching {est_chunks} chunk(s) of {limit} candles each (estimated {est_candles} candles) for interval '{interval}' from {from_} to {to}..."
            )
            fetch_end = end_time
            while True:
                klines = client.klines(
                    symbol=symbol, interval=interval, limit=limit, endTime=fetch_end
                )
                if not klines:
                    break
                # Only keep klines within the start_time
                filtered_klines = [k for k in klines if k[0] >= start_time]
                if not filtered_klines:
                    break
                all_klines = filtered_klines + all_klines
                # Stop if the earliest kline is before start_time
                if klines[0][0] <= start_time:
                    break
                fetch_end = klines[0][0] - 1

        self.write_klines_csv(symbol, path, all_klines)
        abs_path = os.path.abspath(path)
        print(f"Exported symbol={symbol} with {len(all_klines)} rows to {abs_path}.")

    def write_klines_csv(self, symbol, path, all_klines):
        """
        Write kline/candlestick data to CSV.

        Args:
            symbol (str): Symbol name.
            path (str): Output CSV file path.
            all_klines (list): List of kline data.
        """

        resolved_path = file.resolve(path)

        with open(resolved_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "symbol",
                    "date",
                    "start",
                    "end",
                    "open",
                    "high",
                    "low",
                    "close",
                    "vol",
                    "type",
                ]
            )
            for row in all_klines:
                open_time = datetime.datetime.fromtimestamp(
                    row[0] / 1000, tz=datetime.timezone.utc
                )
                close_time = datetime.datetime.fromtimestamp(
                    row[6] / 1000, tz=datetime.timezone.utc
                )
                open_price = float(row[1])
                high_price = float(row[2])
                low_price = float(row[3])
                close_price = float(row[4])
                vol = float(row[5])
                candle_type = 1 if close_price > open_price else 0
                writer.writerow(
                    [
                        symbol,
                        open_time.strftime("%Y-%m-%d"),
                        open_time.strftime("%Y-%m-%d %H:%M:%S"),
                        close_time.strftime("%Y-%m-%d %H:%M:%S"),
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        vol,
                        candle_type,
                    ]
                )


if __name__ == "__main__":
    fire.Fire(Price_CLI)
