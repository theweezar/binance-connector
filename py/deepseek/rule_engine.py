import pandas as pd
import time
from typing import List
from .price_action import PriceAction


class RuleEngine:
    def __init__(self, config):
        self.config = config
        self.price_action = PriceAction(config)

        # Map rule names to their corresponding signal methods
        self.rule_methods = {
            "rsi": self.momentum_rsi_signal,
            # "ma": self.ma_crossover_signal,
            # "bb": self.bollinger_bands_signal,
            "ema": self.ema_crossover_signal,
            "rsi_ma": self.rsi_ma_momentum_signal,
            # "macd": self.macd_signal,
            # "market_structure": self.market_structure_signal,
            # "volume_spike": self._precompute_volume_spike_signals,
            # "volume_distribution": self.volume_distribution_signal,
            # "order_flow": self._precompute_order_flow_imbalance,
        }

    def get_rules(self):
        return self.rule_methods.keys()

    def get_current_signals_dict(self, current_data: pd.Series):
        """
        Extract all rule signals from current data row
        Args:
            current_data: A pandas Series representing one row of data
        Returns:
            Dictionary of {rule_name: signal_value}
        """
        signals = {}
        rules = self.get_rules()
        for rule in rules:
            signal_column = f"signal_{rule}"
            signals[rule] = current_data.get(signal_column, 0)
        return signals

    def momentum_rsi_signal(self, df: pd.DataFrame):
        """Generate RSI Momentum signals: 1 for buy, -1 for sell, 0 for hold"""
        # Initialize signal column with zeros
        signals = pd.Series(0, index=df.index)

        # Calculate previous RSI using shift
        df["prev_rsi"] = df["rsi"].shift(1)

        # Create masks for different conditions
        bullish_cross_mask = (df["rsi"] > self.config.RSI_OVERSOLD) & (
            df["prev_rsi"] <= self.config.RSI_OVERSOLD
        )

        bearish_cross_mask = (df["rsi"] < self.config.RSI_OVERBOUGHT) & (
            df["prev_rsi"] >= self.config.RSI_OVERBOUGHT
        )

        # Apply signals using loc
        signals.loc[bullish_cross_mask] = 1
        signals.loc[bearish_cross_mask] = -1

        # Clean up temporary column
        df.drop("prev_rsi", axis=1, inplace=True)

        return signals.tolist()

    def rsi_ma_momentum_signal(self, df: pd.DataFrame):
        """
        Enhanced RSI signal using RSI MA for trend filtering
        Buy when RSI crosses above RSI_MA and both are below 30 (oversold)
        Sell when RSI crosses below RSI_MA and both are above 70 (overbought)
        """

        # Initialize signal column with zeros
        signals = pd.Series(0, index=df.index)

        # Calculate previous values using shift
        df["prev_rsi"] = df["rsi"].shift(1)
        df["prev_rsi_ma"] = df["rsi_ma"].shift(1)

        # Create masks for the new conditions
        bullish_cross_mask = (
            (df["rsi"] > df["rsi_ma"])
            & (df["prev_rsi"] <= df["prev_rsi_ma"])
            & (df["rsi"] < self.config.RSI_CROSS_OVERSOLD)
            & (df["rsi_ma"] < self.config.RSI_CROSS_OVERSOLD)
        )

        bearish_cross_mask = (
            (df["rsi"] < df["rsi_ma"])
            & (df["prev_rsi"] >= df["prev_rsi_ma"])
            & (df["rsi"] > self.config.RSI_CROSS_OVERBOUGHT)
            & (df["rsi_ma"] > self.config.RSI_CROSS_OVERBOUGHT)
        )

        # Apply signals using loc
        signals.loc[bullish_cross_mask] = 1
        signals.loc[bearish_cross_mask] = -1

        return signals.tolist()

    def ma_crossover_signal(self, df: pd.DataFrame):
        """Generate MA Crossover signals"""
        # Create a copy of the dataframe to avoid modifying the original

        # Initialize signal column with zeros
        signals = pd.Series(0, index=df.index)

        # Calculate previous MA values using shift
        df["prev_ma_short"] = df["ma_short"].shift(1)
        df["prev_ma_long"] = df["ma_long"].shift(1)

        # Create masks for crossover conditions
        bullish_crossover_mask = (df["ma_short"] > df["ma_long"]) & (
            df["prev_ma_short"] <= df["prev_ma_long"]
        )

        bearish_crossover_mask = (df["ma_short"] < df["ma_long"]) & (
            df["prev_ma_short"] >= df["prev_ma_long"]
        )

        # Apply signals using loc
        signals.loc[bullish_crossover_mask] = 1
        signals.loc[bearish_crossover_mask] = -1

        return signals.tolist()

    def ema_crossover_signal(self, df: pd.DataFrame):
        """Generate EMA Crossover signals"""

        # Initialize signal column with zeros
        signals = pd.Series(0, index=df.index)

        # Calculate previous EMA values using shift
        df["prev_ema_short"] = df["ema_short"].shift(1)
        df["prev_ema_long"] = df["ema_long"].shift(1)

        # Create masks for crossover conditions
        bullish_crossover_mask = (df["ema_short"] > df["ema_long"]) & (
            df["prev_ema_short"] <= df["prev_ema_long"]
        )

        bearish_crossover_mask = (df["ema_short"] < df["ema_long"]) & (
            df["prev_ema_short"] >= df["prev_ema_long"]
        )

        # Apply signals using loc
        signals.loc[bullish_crossover_mask] = 1
        signals.loc[bearish_crossover_mask] = -1

        return signals.tolist()

    def bollinger_bands_signal(self, df: pd.DataFrame):
        """Generate Bollinger Bands mean reversion signals"""

        # Initialize signal column with zeros
        signals = pd.Series(0, index=df.index)

        # Create masks for band conditions
        lower_band_touch_mask = df["close"] <= df["bb_lower"]
        upper_band_touch_mask = df["close"] >= df["bb_upper"]

        # Apply signals using loc
        signals.loc[lower_band_touch_mask] = 1
        signals.loc[upper_band_touch_mask] = -1

        return signals.tolist()

    def macd_signal(self, df: pd.DataFrame):
        """
        MACD signal generator
        Buy when MACD crosses above signal, both below 0, and histogram above 0
        Sell when MACD crosses below signal, both above 0, and histogram below 0
        """

        # Initialize signal column with zeros
        signals = pd.Series(0, index=df.index)

        # Calculate previous MACD values using shift
        df["prev_macd"] = df["macd"].shift(1)
        df["prev_macd_signal"] = df["macd_signal"].shift(1)

        # Calculate MACD histogram (MACD - signal)
        df["macd_histogram"] = df["macd"] - df["macd_signal"]
        # df["macd_histogram"] = df["macd_diff"]

        # Create masks for the new conditions
        bullish_crossover_mask = (
            (df["macd"] > df["macd_signal"])
            & (df["prev_macd"] <= df["prev_macd_signal"])
            & (df["macd"] < 0)
            & (df["macd_signal"] < 0)
            & (df["macd_histogram"] > 0)
        )

        bearish_crossover_mask = (
            (df["macd"] < df["macd_signal"])
            & (df["prev_macd"] >= df["prev_macd_signal"])
            & (df["macd"] > 0)
            & (df["macd_signal"] > 0)
            & (df["macd_histogram"] < 0)
        )

        # Apply signals using loc
        signals.loc[bullish_crossover_mask] = 1
        signals.loc[bearish_crossover_mask] = -1

        return signals.tolist()

    def generate_all_signals(self, df: pd.DataFrame):
        """Generate signals for all rules including new ones"""
        temp_df = df.copy()
        rules = self.get_rules()
        # Calculate signals for each rule
        print("\n=== BENCHMARKING ===")
        for rule in rules:
            signal_column = f"signal_{rule}"
            if rule in self.rule_methods:
                start_time = time.perf_counter()
                method = self.rule_methods[rule]
                df[signal_column] = method(temp_df)
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                print(
                    f"-> Function '{method.__name__}' took {execution_time:.4f} seconds to execute."
                )
            else:
                print(f"Warning: No method found for rule '{rule}'")
                df[signal_column] = 0

        return df

    def market_structure_signal(self, df: pd.DataFrame) -> List[float]:
        """Generate market structure signals"""
        signals = []
        for i in range(len(df)):
            signal = self.price_action.get_market_structure_signal(df, i)
            signals.append(signal)
        return signals

    def volume_distribution_signal(self, df: pd.DataFrame) -> List[float]:
        """
        NEW RULE: Volume distribution signals using profile concepts
        """
        signals = []
        for i in range(len(df)):
            signal = self.price_action.get_volume_distribution_signal(df, i)
            signals.append(signal)
        return signals

    def _precompute_volume_spike_signals(self, df: pd.DataFrame):
        """Precompute volume spike signals"""
        volume_threshold = self.config.VOLUME_SPIKE_THRESHOLD

        df["volume_ma"] = df["volume"].rolling(window=20).mean()
        df["volume_spike"] = df["volume"] > df["volume_ma"] * volume_threshold

        # Price acceptance: strong directional move
        df["price_range"] = df["high"] - df["low"]
        df["body_size"] = abs(df["close"] - df["open"])
        df["price_acceptance"] = df["body_size"] / df["price_range"] > 0.6

        # Generate signals
        df["signal_volume_spike"] = 0.0
        bullish_condition = (
            df["volume_spike"] & df["price_acceptance"] & (df["close"] > df["open"])
        )
        bearish_condition = (
            df["volume_spike"] & df["price_acceptance"] & (df["close"] < df["open"])
        )

        df.loc[bullish_condition, "signal_volume_spike"] = 1.0
        df.loc[bearish_condition, "signal_volume_spike"] = -1.0

        signal = df["signal_volume_spike"].to_list()

        return signal

    def _precompute_order_flow_imbalance(self, df: pd.DataFrame):
        """Precompute order flow imbalance"""
        lookback = self.config.ORDER_FLOW_LOOKBACK
        df["buy_volume"] = (df["close"] > df["open"]) * df["volume"]
        df["sell_volume"] = (df["close"] < df["open"]) * df["volume"]
        df["rolling_buy"] = df["buy_volume"].rolling(window=lookback).sum()
        df["rolling_sell"] = df["sell_volume"].rolling(window=lookback).sum()
        df["rolling_total"] = df["rolling_buy"] + df["rolling_sell"]
        df["order_flow_imbalance"] = (df["rolling_buy"] - df["rolling_sell"]) / df[
            "rolling_total"
        ]
        df["order_flow_imbalance"] = df["order_flow_imbalance"].fillna(0.0)

        # Generate signals
        df["signal_order_flow"] = 0.0
        df.loc[df["order_flow_imbalance"] > 0.3, "signal_order_flow"] = 1.0
        df.loc[df["order_flow_imbalance"] < -0.3, "signal_order_flow"] = -1.0

        signal = df["signal_order_flow"].to_list()

        return signal
