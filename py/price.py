import csv
import datetime
import os
import fire
import csv
import datetime
from util import file
from binance.spot import Spot
from termcolor import colored


def calc_stoploss(price: float, stoploss: float):
    """Calculate the stop loss price."""
    return price * (1 - stoploss)


def calc_takeprofit(price: float, takeprofit: float):
    """Calculate the take profit price."""
    return price * (1 + takeprofit)


def calc_pnl(entry_price: float, exit_price: float, quantity: float):
    """
    Calculate profit/loss based on entry and exit prices and quantity.

    Args:
        entry_price (float): Entry price of the position.
        exit_price (float): Exit price of the position.
        quantity (float): Quantity of the asset.

    Returns:
        float: Profit or loss amount.
    """
    return (exit_price - entry_price) * quantity


def calculate_futures_exit_price_full_fund(
    entry_price: float,
    available_fund: float,
    leverage: float,
    target_pnl_percent: float,
    position: str = "long",
):
    """
    Calculate futures exit price using full available fund, leverage, and target PnL %.

    Parameters:
    - entry_price (float): The entry price.
    - available_fund (float): The initial available capital (wallet balance).
    - leverage (float): Leverage multiplier.
    - target_pnl_percent (float): Desired profit in % of margin used.
    - position (str): "long" or "short"

    Returns:
    - exit_price (float): The target exit price to achieve the desired PnL.
    - target_pnl_usd (float): The target profit in USD.
    """

    # Calculate notional size of the position
    notional = available_fund * leverage

    # Calculate quantity (contracts or units of the asset)
    quantity = notional / entry_price

    # Margin used (in this case, it's the full available fund)
    margin_used = available_fund

    # Target PnL in USD
    target_pnl_usd = (target_pnl_percent / 100) * margin_used

    # Price difference needed to reach target PnL
    price_diff = target_pnl_usd / quantity

    # Determine exit price based on position
    if position.lower() == "long":
        exit_price = entry_price + price_diff
    elif position.lower() == "short":
        exit_price = entry_price - price_diff
    else:
        raise ValueError("Position must be 'long' or 'short'")

    return (round(exit_price, 6), round(target_pnl_usd, 2))


class Price_CLI:
    """
    CLI tool to fetch Kline/Candlestick data from Binance and export to CSV.

    Example usage:
        python price.py fetch --symbol=BTCUSDT --interval=1d --path=ignore/btc.csv --chunk=3
        python price.py fetch --symbol=BTCUSDT --interval=1d --path=ignore/btc.csv --from_=2023-01-01 --to=2025-07-12
    """

    limit = 500

    def calc_exit_futures(
        self,
        entry_price: float,
        percent_pnl: float,
        available_fund: float,
        leverage: float,
    ):
        """
        Calculate the exit price when the profit/loss reaches a target value.
        Command: python py/price.py calc_exit_futures --entry_price=3.3830 --percent_pnl=10 --available_fund=50 --leverage=7

        Args:
            entry_price (float): Entry price of the position.
            percent_pnl (float): Target profit or loss amount percent.
            available_fund (float): The initial available capital (wallet balance).
            leverage (float): Leverage multiplier.
        """

        exit_price, target_pnl_usd = calculate_futures_exit_price_full_fund(
            entry_price,
            available_fund,
            leverage,
            percent_pnl
        )

        print(
            colored(
                f"Exit price to achieve {percent_pnl}% PnL: {exit_price} (Target PnL: {target_pnl_usd} USD)",
                "green" if percent_pnl > 0 else "red"
            )
        )

    def calc_end_time_from_to(self, interval: str, from_: str, to: str):
        """
        Calculate candle_ms, est_candles, est_chunks, start_time, end_time for given interval and date range.
        Accepts from_ and to in "%Y-%m-%d %H:%M:%S" or "%Y-%m-%d" format.

        Args:
            interval (str): Kline interval, e.g. "1d", "1h"
            from_ (str): Start date as string
            to (str): End date as string

        Returns:
            tuple: (candle_ms, est_candles, est_chunks, start_time, end_time)
        """
        limit = self.limit

        def parse_date(dt_str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.datetime.strptime(dt_str, fmt)
                except Exception:
                    continue
            raise ValueError(
                'Arguments "from_" and "to" must be in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.'
            )

        from_dt = parse_date(from_)
        to_dt = parse_date(to)
        if from_dt > to_dt:
            raise ValueError('"from_" date must be before or equal to "to" date.')

        start_time = int(
            from_dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
        )
        end_time = int(to_dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
        total_ms = end_time - start_time
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
        return candle_ms, est_candles, est_chunks, start_time, end_time

    def fetch(
        self,
        symbol: str,
        interval: str = "1d",
        path: str = "output.csv",
        chunk: int = None,
        from_: str = None,
        to: str = None,
        merge: str = None,
    ):
        """
        Fetch Kline/Candlestick data from Binance and export to CSV.

        Args:
            symbol (str): Symbol to fetch, e.g. BTCUSDT
            interval (str): Interval, e.g. 1d, 1h, 15m
            path (str): Output CSV file path
            chunk (int): Number of chunks to fetch. Each chunk fetches up to 500 candles (Binance API limit).
            from_ (str): Start date (YYYY-MM-DD), required if chunk is not provided.
            to (str): End date (YYYY-MM-DD), required if chunk is not provided.
            merge (str): If "true", merge new data into existing CSV.
        """
        client = Spot()

        if merge == "true":
            resolved_path = file.resolve(path)
            if os.path.exists(resolved_path):
                self.fetch_and_merge(client, symbol, interval, path)
                print(f"Successfully fetched {symbol}_{interval}")
                return

        if chunk is not None:
            self.fetch_by_chunk(client, symbol, interval, path, chunk)
            print(f"Successfully fetched {symbol}_{interval}")
            return

        if from_ and to:
            self.fetch_by_from_to(client, symbol, interval, path, from_, to)
            print(f"Successfully fetched {symbol}_{interval}")
            return

        raise ValueError(
            'Invalid arguments: provide either "chunk", or both "from_" and "to", or "merge=true".'
        )

    def fetch_and_merge(self, client: Spot, symbol: str, interval: str, path: str):
        """
        Merge new kline data into existing CSV file.

        Args:
            client (Spot): Binance Spot client
            symbol (str): Symbol to fetch, e.g. BTCUSDT
            interval (str): Interval, e.g. 1d, 1h, 15m
            path (str): Output CSV file path
        """
        limit = self.limit
        resolved_path = file.resolve(path)
        with open(resolved_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
        if not rows:
            return  # No data, nothing to merge, fallback to normal fetch
        last_row = rows[-1]
        last_start_str = last_row["start"]
        now_dt = datetime.datetime.now(datetime.timezone.utc)
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        candle_ms, est_candles, est_chunks, fetch_start, fetch_end = (
            self.calc_end_time_from_to(interval, last_start_str, now_str)
        )
        print(
            f"Merging: fetching {est_chunks} chunk(s) of {limit} candles each (estimated {est_candles} candles) for interval '{interval}' from {last_start_str} to now ({now_str})..."
        )
        new_klines = []
        while True:
            klines = client.klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                endTime=fetch_end,
            )
            if not klines:
                print("No more data available.")
                break
            filtered_klines = [k for k in klines if k[0] >= fetch_start]
            if not filtered_klines:
                print("No new data available after last kline.")
                break
            new_klines = filtered_klines + new_klines
            if klines[0][0] <= fetch_start:
                break
            fetch_end = klines[0][0] - 1

        if new_klines:
            last_start_dt = datetime.datetime.strptime(
                last_start_str, "%Y-%m-%d %H:%M:%S"
            )
            last_start_time = int(
                last_start_dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
            )
            # Remove last row if it has the same start time as the first new kline
            dup_rows = [k for k in new_klines if k[0] == last_start_time]
            if dup_rows:
                rows.pop()
                with open(resolved_path, "w", newline="") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)

            self.write_klines_csv(symbol, path, new_klines, append=True)
            abs_path = os.path.abspath(path)
            print(
                f"Merged symbol={symbol} with {len(rows) + len(new_klines)} rows to {abs_path}."
            )
        else:
            print("No new data to merge.")

    def fetch_by_chunk(
        self, client: Spot, symbol: str, interval: str, path: str, chunk: int
    ):
        """
        Fetch Kline/Candlestick data by chunk count and export to CSV.

        Args:
            client (Spot): Binance Spot client
            symbol (str): Symbol to fetch, e.g. BTCUSDT
            interval (str): Interval, e.g. 1d, 1h, 15m
            path (str): Output CSV file path
            chunk (int): Number of chunks to fetch
        """
        limit = self.limit
        all_klines = []
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
        self.write_klines_csv(symbol, path, all_klines)
        abs_path = os.path.abspath(path)
        print(f"Exported symbol={symbol} with {len(all_klines)} rows to {abs_path}.")

    def fetch_by_from_to(
        self, client: Spot, symbol: str, interval: str, path: str, from_: str, to: str
    ):
        """
        Fetch Kline/Candlestick data by date range and export to CSV.

        Args:
            client (Spot): Binance Spot client
            symbol (str): Symbol to fetch, e.g. BTCUSDT
            interval (str): Interval, e.g. 1d, 1h, 15m
            path (str): Output CSV file path
            from_ (str): Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
            to (str): End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
        """
        limit = self.limit
        all_klines = []
        candle_ms, est_candles, est_chunks, start_time, end_time = (
            self.calc_end_time_from_to(interval, from_, to)
        )
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
            filtered_klines = [k for k in klines if k[0] >= start_time]
            if not filtered_klines:
                break
            all_klines = filtered_klines + all_klines
            if klines[0][0] <= start_time:
                break
            fetch_end = klines[0][0] - 1
        self.write_klines_csv(symbol, path, all_klines)
        abs_path = os.path.abspath(path)
        print(f"Exported symbol={symbol} with {len(all_klines)} rows to {abs_path}.")

    def write_klines_csv(
        self, symbol: str, path: str, all_klines: list, append: bool = False
    ):
        """
        Write kline/candlestick data to CSV.

        Args:
            symbol (str): Symbol name.
            path (str): Output CSV file path.
            all_klines (list): List of kline data.
            append (bool): If True, append to file. If False, overwrite.
        """
        headers = [
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
        resolved_path = file.resolve(path)
        mode = "a" if append else "w"
        write_header = not append or not os.path.exists(resolved_path)
        with open(resolved_path, mode, newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            if write_header:
                writer.writeheader()
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
                    {
                        "symbol": symbol,
                        "date": open_time.strftime("%Y-%m-%d"),
                        "start": open_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": close_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "vol": vol,
                        "type": candle_type,
                    }
                )


if __name__ == "__main__":
    fire.Fire(Price_CLI)
