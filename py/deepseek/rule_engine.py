import pandas as pd
import time
from collections import deque
from typing import List, Tuple, Dict


class PriceAction:
    def __init__(self, config):
        self.config = config
        self.support_levels = deque(maxlen=10)  # Keep recent support levels
        self.resistance_levels = deque(maxlen=10)  # Keep recent resistance levels
        self.swing_highs = []
        self.swing_lows = []

    def detect_market_structure(
        self, df: pd.DataFrame
    ) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """
        Detect market structure shifts using swing point analysis

        Returns:
            Tuple of (swing_highs, swing_lows)
        """
        swing_length = self.config.SWING_POINT_LENGTH
        swing_highs = []
        swing_lows = []

        for i in range(swing_length, len(df) - swing_length):
            current_high = df["high"].iloc[i]
            current_low = df["low"].iloc[i]

            # Check for swing high
            left_highs = [df["high"].iloc[i - j] for j in range(1, swing_length + 1)]
            right_highs = [df["high"].iloc[i + j] for j in range(1, swing_length + 1)]

            if all(current_high > high for high in left_highs) and all(
                current_high > high for high in right_highs
            ):
                swing_highs.append((i, current_high))

            # Check for swing low
            left_lows = [df["low"].iloc[i - j] for j in range(1, swing_length + 1)]
            right_lows = [df["low"].iloc[i + j] for j in range(1, swing_length + 1)]

            if all(current_low < low for low in left_lows) and all(
                current_low < low for low in right_lows
            ):
                swing_lows.append((i, current_low))

        self.swing_highs = swing_highs
        self.swing_lows = swing_lows
        return swing_highs, swing_lows

    def calculate_volume_profile(
        self, df: pd.DataFrame, lookback: int = 50
    ) -> Dict[float, float]:
        """
        NEW RULE: Calculate volume profile distribution
        Returns dictionary: {price_level: total_volume}
        """
        if len(df) < lookback:
            lookback = len(df)

        recent_data = df.iloc[-lookback:]
        price_range = recent_data["high"].max() - recent_data["low"].min()
        num_bins = 20
        bin_size = price_range / num_bins
        min_price = recent_data["low"].min()

        volume_profile = {}

        for i in range(num_bins):
            price_level = min_price + (i * bin_size) + (bin_size / 2)
            mask = (recent_data["low"] <= price_level + bin_size / 2) & (
                recent_data["high"] >= price_level - bin_size / 2
            )
            volume_at_level = recent_data[mask]["volume"].sum()
            volume_profile[price_level] = volume_at_level

        return volume_profile

    def volume_distribution_analysis(
        self, df: pd.DataFrame, current_index: int
    ) -> List[Tuple[str, int]]:
        """
        NEW RULE: Volume distribution analysis using volume profile concepts
        This analyzes POC (Point of Control) and Value Area
        """
        signals = []
        lookback = self.config.VOLUME_PROFILE_LOOKBACK
        lookback_data = df.iloc[current_index - lookback : current_index]
        volume_profile = self.calculate_volume_profile(lookback_data, lookback)

        if not volume_profile:
            return signals

        # Find Point of Control (POC)
        poc_price = max(volume_profile.items(), key=lambda x: x[1])[0]
        current_price = df["close"].iloc[current_index]
        current_volume = df["volume"].iloc[current_index]
        avg_volume = lookback_data["volume"].mean()

        # Calculate Value Area (price levels containing 70% of volume)
        total_volume = sum(volume_profile.values())
        sorted_levels = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)

        cumulative_volume = 0
        value_area_prices = []

        for price, volume in sorted_levels:
            cumulative_volume += volume
            value_area_prices.append(price)
            if cumulative_volume / total_volume >= 0.7:
                break

        # Generate volume distribution signals
        poc_distance = abs(current_price - poc_price) / current_price
        volume_spike = current_volume > avg_volume * self.config.VOLUME_SPIKE_THRESHOLD

        # Signal 1: Price at POC with volume confirmation
        if poc_distance < 0.005 and volume_spike:
            if current_price > df["open"].iloc[current_index]:
                signals.append(("buy_poc", current_index))
            else:
                signals.append(("sell_poc", current_index))

        # Signal 2: Price breakout from value area
        min_value_area = min(value_area_prices) if value_area_prices else current_price
        max_value_area = max(value_area_prices) if value_area_prices else current_price

        if current_price > max_value_area and volume_spike:
            signals.append(("breakout_above_va", current_index))
        elif current_price < min_value_area and volume_spike:
            signals.append(("breakout_below_va", current_index))

        return signals

    def get_market_structure_signal(
        self, df: pd.DataFrame, current_index: int
    ) -> float:
        """Generate market structure trading signal"""
        if current_index < self.config.SWING_POINT_LENGTH * 2:
            return 0.0

        swing_highs, swing_lows = self.detect_market_structure(df.iloc[:current_index])
        current_price = df["close"].iloc[current_index]

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return 0.0

        # Check for higher highs/lows (uptrend) or lower highs/lows (downtrend)
        latest_high = swing_highs[-1][1] if swing_highs else current_price
        prev_high = swing_highs[-2][1] if len(swing_highs) >= 2 else latest_high
        latest_low = swing_lows[-1][1] if swing_lows else current_price
        prev_low = swing_lows[-2][1] if len(swing_lows) >= 2 else latest_low

        if latest_high > prev_high and latest_low > prev_low:
            return 1.0  # Uptrend
        elif latest_high < prev_high and latest_low < prev_low:
            return -1.0  # Downtrend
        else:
            return 0.0  # Range or unclear

    def get_volume_distribution_signal(
        self, df: pd.DataFrame, current_index: int
    ) -> float:
        """
        NEW RULE: Volume distribution trading signal
        """
        if current_index < self.config.VOLUME_PROFILE_LOOKBACK:
            return 0.0

        signals = self.volume_distribution_analysis(df, current_index)
        if not signals:
            return 0.0

        latest_signal_type, _ = signals[-1]

        if latest_signal_type in ["buy_poc", "breakout_above_va"]:
            return 1.0
        elif latest_signal_type in ["sell_poc", "breakout_below_va"]:
            return -1.0
        else:
            return 0.0


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
            "macd": self.macd_signal,
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
        # Create a copy of the dataframe to avoid modifying the original
        temp_df = df.copy()

        # Initialize signal column with zeros
        signals = pd.Series(0, index=temp_df.index)

        # Calculate previous values using shift
        temp_df["prev_rsi"] = temp_df["rsi"].shift(1)
        temp_df["prev_rsi_ma"] = temp_df["rsi_ma"].shift(1)

        # Create masks for the new conditions
        bullish_cross_mask = (
            (temp_df["rsi"] > temp_df["rsi_ma"])
            & (temp_df["prev_rsi"] <= temp_df["prev_rsi_ma"])
            & (temp_df["rsi"] < self.config.RSI_CROSS_OVERSOLD)
            & (temp_df["rsi_ma"] < self.config.RSI_CROSS_OVERSOLD)
        )

        bearish_cross_mask = (
            (temp_df["rsi"] < temp_df["rsi_ma"])
            & (temp_df["prev_rsi"] >= temp_df["prev_rsi_ma"])
            & (temp_df["rsi"] > self.config.RSI_CROSS_OVERBOUGHT)
            & (temp_df["rsi_ma"] > self.config.RSI_CROSS_OVERBOUGHT)
        )

        # Apply signals using loc
        signals.loc[bullish_cross_mask] = 1
        signals.loc[bearish_cross_mask] = -1

        return signals.tolist()

    def ma_crossover_signal(self, df: pd.DataFrame):
        """Generate MA Crossover signals"""
        # Create a copy of the dataframe to avoid modifying the original
        temp_df = df.copy()

        # Initialize signal column with zeros
        signals = pd.Series(0, index=temp_df.index)

        # Calculate previous MA values using shift
        temp_df["prev_ma_short"] = temp_df["ma_short"].shift(1)
        temp_df["prev_ma_long"] = temp_df["ma_long"].shift(1)

        # Create masks for crossover conditions
        bullish_crossover_mask = (temp_df["ma_short"] > temp_df["ma_long"]) & (
            temp_df["prev_ma_short"] <= temp_df["prev_ma_long"]
        )

        bearish_crossover_mask = (temp_df["ma_short"] < temp_df["ma_long"]) & (
            temp_df["prev_ma_short"] >= temp_df["prev_ma_long"]
        )

        # Apply signals using loc
        signals.loc[bullish_crossover_mask] = 1
        signals.loc[bearish_crossover_mask] = -1

        return signals.tolist()

    def ema_crossover_signal(self, df: pd.DataFrame):
        """Generate EMA Crossover signals"""
        # Create a copy of the dataframe to avoid modifying the original
        temp_df = df.copy()

        # Initialize signal column with zeros
        signals = pd.Series(0, index=temp_df.index)

        # Calculate previous EMA values using shift
        temp_df["prev_ema_short"] = temp_df["ema_short"].shift(1)
        temp_df["prev_ema_long"] = temp_df["ema_long"].shift(1)

        # Create masks for crossover conditions
        bullish_crossover_mask = (temp_df["ema_short"] > temp_df["ema_long"]) & (
            temp_df["prev_ema_short"] <= temp_df["prev_ema_long"]
        )

        bearish_crossover_mask = (temp_df["ema_short"] < temp_df["ema_long"]) & (
            temp_df["prev_ema_short"] >= temp_df["prev_ema_long"]
        )

        # Apply signals using loc
        signals.loc[bullish_crossover_mask] = 1
        signals.loc[bearish_crossover_mask] = -1

        return signals.tolist()

    def bollinger_bands_signal(self, df: pd.DataFrame):
        """Generate Bollinger Bands mean reversion signals"""
        # Create a copy of the dataframe to avoid modifying the original
        temp_df = df.copy()

        # Initialize signal column with zeros
        signals = pd.Series(0, index=temp_df.index)

        # Create masks for band conditions
        lower_band_touch_mask = temp_df["close"] <= temp_df["bb_lower"]
        upper_band_touch_mask = temp_df["close"] >= temp_df["bb_upper"]

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
        # Create a copy of the dataframe to avoid modifying the original
        temp_df = df.copy()

        # Initialize signal column with zeros
        signals = pd.Series(0, index=temp_df.index)

        # Calculate previous MACD values using shift
        temp_df["prev_macd"] = temp_df["macd"].shift(1)
        temp_df["prev_macd_signal"] = temp_df["macd_signal"].shift(1)

        # Calculate MACD histogram (MACD - signal)
        temp_df["macd_histogram"] = temp_df["macd"] - temp_df["macd_signal"]
        # temp_df["macd_histogram"] = temp_df["macd_diff"]

        # Create masks for the new conditions
        bullish_crossover_mask = (
            (temp_df["macd"] > temp_df["macd_signal"])
            & (temp_df["prev_macd"] <= temp_df["prev_macd_signal"])
            & (temp_df["macd"] < 0)
            & (temp_df["macd_signal"] < 0)
            & (temp_df["macd_histogram"] > 0)
        )

        bearish_crossover_mask = (
            (temp_df["macd"] < temp_df["macd_signal"])
            & (temp_df["prev_macd"] >= temp_df["prev_macd_signal"])
            & (temp_df["macd"] > 0)
            & (temp_df["macd_signal"] > 0)
            & (temp_df["macd_histogram"] < 0)
        )

        # Apply signals using loc
        signals.loc[bullish_crossover_mask] = 1
        signals.loc[bearish_crossover_mask] = -1

        return signals.tolist()

    def generate_all_signals(self, df: pd.DataFrame):
        """Generate signals for all rules including new ones"""
        df = df.copy()
        rules = self.get_rules()
        # Calculate signals for each rule
        print("\n=== BENCHMARKING ===")
        for rule in rules:
            if rule in self.rule_methods:
                start_time = time.perf_counter()
                method = self.rule_methods[rule]
                signal_column = f"signal_{rule}"
                df[signal_column] = method(df)
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                print(
                    f"-> Function '{method.__name__}' took {execution_time:.4f} seconds to execute."
                )
            else:
                print(f"Warning: No method found for rule '{rule}'")
                df[f"signal_{rule}"] = 0

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

        _df = df.copy()

        _df["volume_ma"] = _df["volume"].rolling(window=20).mean()
        _df["volume_spike"] = _df["volume"] > _df["volume_ma"] * volume_threshold

        # Price acceptance: strong directional move
        _df["price_range"] = _df["high"] - _df["low"]
        _df["body_size"] = abs(_df["close"] - _df["open"])
        _df["price_acceptance"] = _df["body_size"] / _df["price_range"] > 0.6

        # Generate signals
        _df["signal_volume_spike"] = 0.0
        bullish_condition = (
            _df["volume_spike"] & _df["price_acceptance"] & (_df["close"] > _df["open"])
        )
        bearish_condition = (
            _df["volume_spike"] & _df["price_acceptance"] & (_df["close"] < _df["open"])
        )

        _df.loc[bullish_condition, "signal_volume_spike"] = 1.0
        _df.loc[bearish_condition, "signal_volume_spike"] = -1.0

        signal = _df["signal_volume_spike"].to_list()

        return signal

    def _precompute_order_flow_imbalance(self, df: pd.DataFrame):
        """Precompute order flow imbalance"""
        lookback = self.config.ORDER_FLOW_LOOKBACK
        _df = df.copy()
        _df["buy_volume"] = (_df["close"] > _df["open"]) * _df["volume"]
        _df["sell_volume"] = (_df["close"] < _df["open"]) * _df["volume"]
        _df["rolling_buy"] = _df["buy_volume"].rolling(window=lookback).sum()
        _df["rolling_sell"] = _df["sell_volume"].rolling(window=lookback).sum()
        _df["rolling_total"] = _df["rolling_buy"] + _df["rolling_sell"]
        _df["order_flow_imbalance"] = (_df["rolling_buy"] - _df["rolling_sell"]) / _df[
            "rolling_total"
        ]
        _df["order_flow_imbalance"] = _df["order_flow_imbalance"].fillna(0.0)

        # Generate signals
        _df["signal_order_flow"] = 0.0
        _df.loc[_df["order_flow_imbalance"] > 0.3, "signal_order_flow"] = 1.0
        _df.loc[_df["order_flow_imbalance"] < -0.3, "signal_order_flow"] = -1.0

        signal = _df["signal_order_flow"].to_list()

        return signal
