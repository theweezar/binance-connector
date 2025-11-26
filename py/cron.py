import time
import winsound
import ta.momentum
from pathlib import Path
from fire import Fire
from .bingx import BingX_CLI
from .util import file
from .telegrambot import send_telegram_message


def notify():
    try:
        for _ in range(3):
            winsound.Beep(1000, 300)
            time.sleep(0.1)
    except Exception:
        for _ in range(3):
            print("\a", end="", flush=True)
            time.sleep(0.2)


def run_job(symbol: str, interval: str):
    repo_root = Path(__file__).resolve().parents[1]

    # Hard-coded parameters (per request)
    df_name = f"{symbol}_{interval}"

    output_csv = str(repo_root / "ignore" / f"{df_name}.csv")
    b_cli = BingX_CLI(symbol=symbol, interval=interval, output=output_csv, chunk=1)
    b_cli.run()

    input_path = output_csv
    df = file.get_source(input_path)
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=9).rsi()

    oversold = 30.0
    overbought = 70.0

    # last row
    last = df.iloc[-1]
    rsi_value = float(last["rsi"])
    price = float(last["close"])

    alert = False
    if rsi_value < oversold or rsi_value > overbought:
        alert = True

    if alert:
        if rsi_value < oversold:
            msg = f"🔴 Warning: {symbol} {interval} oversold: rsi={rsi_value:.2f}, price={price:.2f}."
        if rsi_value > overbought:
            msg = f"🟢 Warning: {symbol} {interval} overbought: rsi={rsi_value:.2f}, price={price:.2f}."

        send_telegram_message(msg)
        notify()
    else:
        print(f"[cron]: rsi={rsi_value:.2f}, price={price:.2f} - no alert.")


class Cron_CLI:
    def __init__(self, symbol: str, interval: str):
        self.symbol = symbol
        self.interval = interval

    def run(self):
        run_job(self.symbol, self.interval)


if __name__ == "__main__":
    # python -m py.cron run --symbol=XAUT-USDT --interval=5m
    Fire(Cron_CLI)
