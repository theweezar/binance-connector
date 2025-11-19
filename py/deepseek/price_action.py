import pandas as pd
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
