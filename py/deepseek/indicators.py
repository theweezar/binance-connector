import ta
import ta.momentum
import ta.trend
import ta.volatility
import pandas as pd


class Indicators:
    def __init__(self, config):
        self.config = config

    def calculate_all_indicators(self, df: pd.DataFrame):
        """Calculate all technical indicators including new ones"""
        df = df.copy()

        # Existing indicators
        df = self._calculate_basic_indicators(df)

        # New indicators
        df = self._calculate_ema_indicators(df)
        df = self._calculate_rsi_ma(df)
        df = self._calculate_price_action_indicators(df)
        df = self._calculate_macd(df)

        return df

    def _calculate_basic_indicators(self, df: pd.DataFrame):
        """Calculate existing basic indicators"""
        # RSI
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

    def _calculate_ema_indicators(self, df: pd.DataFrame):
        """Calculate EMA indicators"""
        df["ema_short"] = ta.trend.EMAIndicator(
            df["close"], window=self.config.EMA_SHORT
        ).ema_indicator()

        df["ema_long"] = ta.trend.EMAIndicator(
            df["close"], window=self.config.EMA_LONG
        ).ema_indicator()

        return df

    def _calculate_rsi_ma(self, df: pd.DataFrame):
        """Calculate Moving Average of RSI"""
        if self.config.RSI_MA_METHOD == "sma":
            df["rsi_ma"] = ta.trend.SMAIndicator(
                df["rsi"], window=self.config.RSI_MA_PERIOD
            ).sma_indicator()

        if self.config.RSI_MA_METHOD == "ema":
            df["rsi_ma"] = ta.trend.EMAIndicator(
                df["rsi"], window=self.config.RSI_MA_PERIOD
            ).ema_indicator()

        return df

    def _calculate_macd(self, df: pd.DataFrame):
        """Calculate MACD indicators"""
        # Calculate MACD line
        # Calculate MACD signal line
        # Calculate MACD histogram
        df["macd"] = ta.trend.macd(
            df["close"],
            window_slow=self.config.MACD_SLOW,
            window_fast=self.config.MACD_FAST,
        )
        df["macd_signal"] = ta.trend.macd_signal(
            df["close"],
            window_slow=self.config.MACD_SLOW,
            window_fast=self.config.MACD_FAST,
            window_sign=self.config.MACD_SIGN,
        )
        df["macd_diff"] = ta.trend.macd_diff(
            df["close"],
            window_slow=self.config.MACD_SLOW,
            window_fast=self.config.MACD_FAST,
            window_sign=self.config.MACD_SIGN,
        )

        return df

    def _calculate_price_action_indicators(self, df: pd.DataFrame):
        """Calculate price action indicators"""
        # Volume moving average
        df["volume_ma"] = (
            df["volume"].rolling(window=self.config.VOLUME_MA_PERIOD).mean()
        )

        # Volume strength
        df["volume_strength"] = df["volume"] / df["volume_ma"]

        return df
