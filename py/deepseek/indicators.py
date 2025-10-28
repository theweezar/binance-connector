import pandas as pd
import ta
from config import Config


class Indicators:
    def __init__(self, config):
        self.config = config

    def calculate_all_indicators(self, df):
        """Calculate all technical indicators for the dataframe"""
        df = df.copy()

        # RSI Momentum
        df["rsi"] = ta.momentum.RSIIndicator(
            df["close"], window=self.config.RSI_PERIOD
        ).rsi()

        # Moving Average Crossover
        df["ma_short"] = ta.trend.SMAIndicator(
            df["close"], window=self.config.MA_SHORT
        ).sma_indicator()
        df["ma_long"] = ta.trend.SMAIndicator(
            df["close"], window=self.config.MA_LONG
        ).sma_indicator()

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(
            df["close"], window=self.config.BB_PERIOD, window_dev=self.config.BB_STD
        )
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()
        df["bb_middle"] = bb.bollinger_mavg()

        return df
