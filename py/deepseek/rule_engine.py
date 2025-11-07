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

    def identify_supply_demand_zones(
        self, df: pd.DataFrame, lookback: int = 20, min_strength: float = 2.0
    ) -> List[Tuple[str, float, int]]:
        """
        Identify supply/demand zones based on price rejection and volume

        Returns:
            List of tuples: (zone_type, price_level, index)
        """
        zones = []
        for i in range(lookback, len(df) - lookback):
            current = df.iloc[i]
            body_size = abs(current["close"] - current["open"])

            if body_size == 0:  # Avoid division by zero
                continue

            # Check for supply zone (bearish rejection)
            upper_wick_ratio = (
                current["high"] - max(current["open"], current["close"])
            ) / body_size
            if current["close"] < current["open"] and upper_wick_ratio > min_strength:
                zones.append(("supply", current["high"], i))

            # Check for demand zone (bullish rejection)
            lower_wick_ratio = (
                min(current["open"], current["close"]) - current["low"]
            ) / body_size
            if current["close"] > current["open"] and lower_wick_ratio > min_strength:
                zones.append(("demand", current["low"], i))

        return zones

    def detect_market_structure(
        self, df: pd.DataFrame, swing_length: int = 5
    ) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """
        Detect market structure shifts using swing point analysis

        Returns:
            Tuple of (swing_highs, swing_lows)
        """
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

    def volume_spike_analysis(
        self, df: pd.DataFrame, volume_threshold: float = 1.5
    ) -> List[Tuple[str, int]]:
        """
        ORIGINAL RULE: Volume spike analysis for breakout confirmation
        This detects high volume breakouts with price acceptance
        """
        signals = []
        for i in range(1, len(df)):
            current = df.iloc[i]
            prev = df.iloc[i - 1]

            # High volume breakout with price acceptance
            volume_spike = current["volume"] > prev["volume"] * volume_threshold
            if current["high"] - current["low"] > 0:
                price_acceptance = (
                    abs(current["close"] - current["open"])
                    / (current["high"] - current["low"])
                    > 0.6
                )
            else:
                price_acceptance = False

            if volume_spike and price_acceptance:
                if current["close"] > current["open"]:
                    signals.append(("buy_acceptance", i))
                else:
                    signals.append(("sell_acceptance", i))

        return signals

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

        if current_index < self.config.VOLUME_PROFILE_LOOKBACK:
            return signals

        lookback_data = df.iloc[
            current_index - self.config.VOLUME_PROFILE_LOOKBACK : current_index
        ]
        volume_profile = self.calculate_volume_profile(
            lookback_data, self.config.VOLUME_PROFILE_LOOKBACK
        )

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

    def order_flow_imbalance(self, df: pd.DataFrame, lookback: int = 10) -> List[float]:
        """
        Calculate order flow imbalance using price-volume relationship

        Returns:
            List of imbalance values (-1 to +1)
        """
        imbalances = []
        for i in range(lookback, len(df)):
            recent = df.iloc[i - lookback : i]

            # Calculate buying vs selling pressure
            buy_volume = recent[recent["close"] > recent["open"]]["volume"].sum()
            sell_volume = recent[recent["close"] < recent["open"]]["volume"].sum()

            total_volume = buy_volume + sell_volume
            if total_volume > 0:
                imbalance = (buy_volume - sell_volume) / total_volume
                imbalances.append(imbalance)
            else:
                imbalances.append(0.0)

        return imbalances

    def get_supply_demand_signal(self, df: pd.DataFrame, current_index: int) -> float:
        """Generate supply/demand zone trading signal"""
        if current_index < self.config.SUPPLY_DEMAND_LOOKBACK:
            return 0.0

        zones = self.identify_supply_demand_zones(df.iloc[:current_index])
        current_price = df["close"].iloc[current_index]

        signal = 0.0
        for zone_type, price_level, _ in zones[-5:]:  # Check recent 5 zones
            distance_pct = abs(current_price - price_level) / current_price

            if distance_pct < 0.005:  # Within 0.5% of zone
                if zone_type == "demand":
                    signal = 1.0
                else:  # supply
                    signal = -1.0
                break

        return signal

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

    def get_volume_spike_signal(self, df: pd.DataFrame, current_index: int) -> float:
        """
        ORIGINAL RULE: Volume spike trading signal
        """
        if current_index < 2:
            return 0.0

        signals = self.volume_spike_analysis(df.iloc[:current_index])
        if not signals:
            return 0.0

        recent_signals = [s for s in signals if s[1] >= current_index - 5]
        if not recent_signals:
            return 0.0

        latest_signal_type, _ = recent_signals[-1]
        return 1.0 if latest_signal_type == "buy_acceptance" else -1.0

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

    def get_order_flow_signal(self, df: pd.DataFrame, current_index: int) -> float:
        """Generate order flow imbalance trading signal"""
        if current_index < self.config.ORDER_FLOW_LOOKBACK:
            return 0.0

        imbalances = self.order_flow_imbalance(
            df.iloc[:current_index], self.config.ORDER_FLOW_LOOKBACK
        )
        if not imbalances:
            return 0.0

        current_imbalance = imbalances[-1]

        # Convert imbalance to trading signal
        if current_imbalance > 0.3:
            return 1.0  # Strong buying pressure
        elif current_imbalance < -0.3:
            return -1.0  # Strong selling pressure
        else:
            return 0.0

    def find_pivot_points(self, df: pd.DataFrame, window=5):
        """
        Find local pivot highs and lows using proper DataFrame indexing
        Args:
            df: DataFrame with 'high' and 'low' columns
            window: number of bars on each side to consider
        """
        pivot_highs = []
        pivot_lows = []

        # Use integer-based indexing with iloc
        for i in range(window, len(df) - window):
            current_high = df["high"].iloc[i]
            current_low = df["low"].iloc[i]

            # Check left and right windows for highs
            left_highs = [df["high"].iloc[i - j] for j in range(1, window + 1)]
            right_highs = [df["high"].iloc[i + j] for j in range(1, window + 1)]

            # Check left and right windows for lows
            left_lows = [df["low"].iloc[i - j] for j in range(1, window + 1)]
            right_lows = [df["low"].iloc[i + j] for j in range(1, window + 1)]

            # Check for pivot high (higher than all in window)
            if all(current_high > high for high in left_highs) and all(
                current_high > high for high in right_highs
            ):
                pivot_highs.append((i, current_high))

            # Check for pivot low (lower than all in window)
            if all(current_low < low for low in left_lows) and all(
                current_low < low for low in right_lows
            ):
                pivot_lows.append((i, current_low))

        return pivot_highs, pivot_lows

    def calculate_support_resistance(self, df: pd.DataFrame, lookback_period=20):
        """
        Calculate dynamic support and resistance levels
        Returns: current_support, current_resistance, strength_signal
        """
        if len(df) < lookback_period:
            return None, None, 0

        recent_highs = df["high"].tail(lookback_period)
        recent_lows = df["low"].tail(lookback_period)

        # Find recent pivot points
        pivot_highs, pivot_lows = self.find_pivot_points(df, window=3)

        if pivot_highs:
            current_resistance = max(
                [ph[1] for ph in pivot_highs[-3:]]
            )  # Last 3 resistance points
            resistance_strength = len(
                [ph for ph in pivot_highs if ph[1] >= current_resistance * 0.99]
            )
        else:
            current_resistance = recent_highs.max()
            resistance_strength = 1

        if pivot_lows:
            current_support = min(
                [pl[1] for pl in pivot_lows[-3:]]
            )  # Last 3 support points
            support_strength = len(
                [pl for pl in pivot_lows if pl[1] <= current_support * 1.01]
            )
        else:
            current_support = recent_lows.min()
            support_strength = 1

        # Store levels for future reference
        if current_support:
            self.support_levels.append(current_support)
        if current_resistance:
            self.resistance_levels.append(current_resistance)

        # Calculate strength signal (-1 to +1)
        current_price = df["close"].iloc[-1]
        strength_signal = 0

        # Bullish if near support with volume
        support_distance = (
            abs(current_price - current_support) / current_support
            if current_support
            else 1
        )
        resistance_distance = (
            abs(current_price - current_resistance) / current_resistance
            if current_resistance
            else 1
        )

        if support_distance < 0.005:  # Within 0.5% of support
            strength_signal = 1.0
        elif resistance_distance < 0.005:  # Within 0.5% of resistance
            strength_signal = -1.0
        elif current_price > (
            current_support + (current_resistance - current_support) * 0.6
        ):
            # In upper 40% of range
            strength_signal = -0.5
        elif current_price < (
            current_support + (current_resistance - current_support) * 0.4
        ):
            # In lower 40% of range
            strength_signal = 0.5

        return current_support, current_resistance, strength_signal

    def get_price_action_signal(self, df: pd.DataFrame, current_index):
        """
        Generate price action signal combining support/resistance and volume
        """
        if current_index < self.config.SUPPORT_RESISTANCE_LOOKBACK:
            return 0

        # Get recent data for analysis
        recent_data = df.iloc[
            current_index - self.config.SUPPORT_RESISTANCE_LOOKBACK : current_index
        ]

        support, resistance, level_signal = self.calculate_support_resistance(
            recent_data, self.config.SUPPORT_RESISTANCE_LOOKBACK
        )

        if support is None or resistance is None:
            return 0

        current_price = df["close"].iloc[current_index]
        current_volume = df["volume"].iloc[current_index]
        volume_ma = df["volume_ma"].iloc[current_index]

        volume_strength = current_volume / volume_ma if volume_ma > 0 else 1

        # Combined signal logic
        final_signal = 0

        # Strong buy: near support with high volume
        if level_signal > 0 and volume_strength > self.config.MIN_VOLUME_STRENGTH:
            final_signal = 1.0
        # Strong sell: near resistance with high volume
        elif level_signal < 0 and volume_strength > self.config.MIN_VOLUME_STRENGTH:
            final_signal = -1.0
        # Moderate signals
        elif level_signal > 0.5:
            final_signal = 0.5
        elif level_signal < -0.5:
            final_signal = -0.5

        return final_signal


class RuleEngine:
    def __init__(self, config):
        self.config = config
        self.price_action = PriceAction(config)

        # Map rule names to their corresponding signal methods
        self.rule_methods = {
            "rsi": self.momentum_rsi_signal,
            # "ma": self.ma_crossover_signal,
            "bb": self.bollinger_bands_signal,
            "ema": self.ema_crossover_signal,
            "rsi_ma": self.rsi_ma_momentum_signal,
            # "price_action": self.price_action_signal,
            # "supply_demand": self.supply_demand_signal,
            # "market_structure": self.market_structure_signal,
            # "volume_spike": self.volume_spike_signal,  # ORIGINAL
            # "volume_distribution": self.volume_distribution_signal,  # NEW
            # "order_flow": self.order_flow_signal
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
        signals = []
        for i in range(len(df)):
            if i < 1:
                signals.append(0)
                continue

            rsi = df["rsi"].iloc[i]
            prev_rsi = df["rsi"].iloc[i - 1]

            # Bullish momentum: RSI crosses above oversold or shows upward momentum from oversold
            if (
                rsi > self.config.RSI_OVERSOLD and prev_rsi <= self.config.RSI_OVERSOLD
            ) or (rsi > self.config.RSI_OVERSOLD and rsi > prev_rsi):
                signals.append(1)
            # Bearish momentum: RSI crosses below overbought or shows downward momentum from overbought
            elif (
                rsi < self.config.RSI_OVERBOUGHT
                and prev_rsi >= self.config.RSI_OVERBOUGHT
            ) or (rsi < self.config.RSI_OVERBOUGHT and rsi < prev_rsi):
                signals.append(-1)
            else:
                signals.append(0)

        return signals

    def rsi_ma_momentum_signal(self, df):
        """
        Enhanced RSI signal using RSI MA for trend filtering
        Buy when RSI > RSI_MA and RSI is rising from oversold
        Sell when RSI < RSI_MA and RSI is falling from overbought
        """
        signals = []
        for i in range(len(df)):
            if i < 2:
                signals.append(0)
                continue

            rsi = df["rsi"].iloc[i]
            rsi_ma = df["rsi_ma"].iloc[i]
            prev_rsi = df["rsi"].iloc[i - 1]
            prev_rsi_ma = df["rsi_ma"].iloc[i - 1]

            rsi_trend = rsi - prev_rsi
            rsi_ma_trend = rsi_ma - prev_rsi_ma

            # Bullish: RSI above its MA and both rising, coming from oversold
            if (
                rsi > rsi_ma
                and rsi_trend > 0
                and rsi_ma_trend > 0
                and prev_rsi <= self.config.RSI_OVERSOLD
            ):
                signals.append(1)
            # Bearish: RSI below its MA and both falling, coming from overbought
            elif (
                rsi < rsi_ma
                and rsi_trend < 0
                and rsi_ma_trend < 0
                and prev_rsi >= self.config.RSI_OVERBOUGHT
            ):
                signals.append(-1)
            # Moderate bullish: RSI crossing above its MA
            elif rsi > rsi_ma and prev_rsi <= prev_rsi_ma:
                signals.append(0.5)
            # Moderate bearish: RSI crossing below its MA
            elif rsi < rsi_ma and prev_rsi >= prev_rsi_ma:
                signals.append(-0.5)
            else:
                signals.append(0)

        return signals

    def ma_crossover_signal(self, df: pd.DataFrame):
        """Generate MA Crossover signals"""
        signals = []
        for i in range(len(df)):
            if i < 1:
                signals.append(0)
                continue

            ma_short = df["ma_short"].iloc[i]
            ma_long = df["ma_long"].iloc[i]
            prev_ma_short = df["ma_short"].iloc[i - 1]
            prev_ma_long = df["ma_long"].iloc[i - 1]

            # Golden cross
            if (ma_short > ma_long) and (prev_ma_short <= prev_ma_long):
                signals.append(1)
            # Death cross
            elif (ma_short < ma_long) and (prev_ma_short >= prev_ma_long):
                signals.append(-1)
            else:
                signals.append(0)

        return signals

    def ema_crossover_signal(self, df: pd.DataFrame):
        """Generate EMA Crossover signals (more responsive than SMA)"""
        signals = []
        for i in range(len(df)):
            if i < 1:
                signals.append(0)
                continue

            ema_short = df["ema_short"].iloc[i]
            ema_long = df["ema_long"].iloc[i]
            prev_ema_short = df["ema_short"].iloc[i - 1]
            prev_ema_long = df["ema_long"].iloc[i - 1]

            # Bullish crossover
            if (ema_short > ema_long) and (prev_ema_short <= prev_ema_long):
                signals.append(1)
            # Bearish crossover
            elif (ema_short < ema_long) and (prev_ema_short >= prev_ema_long):
                signals.append(-1)
            else:
                signals.append(0)

        return signals

    def bollinger_bands_signal(self, df: pd.DataFrame):
        """Generate Bollinger Bands mean reversion signals"""
        signals = []
        for i in range(len(df)):
            close = df["close"].iloc[i]
            bb_upper = df["bb_upper"].iloc[i]
            bb_lower = df["bb_lower"].iloc[i]
            bb_middle = df["bb_middle"].iloc[i]

            # Buy when price touches lower band
            if close <= bb_lower:
                signals.append(1)
            # Sell when price touches upper band
            elif close >= bb_upper:
                signals.append(-1)
            else:
                signals.append(0)

        return signals

    def price_action_signal(self, df: pd.DataFrame):
        """Generate price action signals using support/resistance and volume"""
        signals = []
        for i in range(len(df)):
            signal = self.price_action.get_price_action_signal(df, i)
            signals.append(signal)

        return signals

    def generate_all_signals(self, df: pd.DataFrame):
        """Generate signals for all rules including new ones"""
        df = df.copy()
        rules = self.get_rules()
        # Calculate signals for each rule
        for rule in rules:
            if rule in self.rule_methods:
                method = self.rule_methods[rule]
                signal_column = f"signal_{rule}"
                df[signal_column] = method(df)
            else:
                print(f"Warning: No method found for rule '{rule}'")
                df[f"signal_{rule}"] = 0

        return df

    def supply_demand_signal(self, df: pd.DataFrame) -> List[float]:
        """Generate supply/demand zone signals"""
        signals = []
        for i in range(len(df)):
            signal = self.price_action.get_supply_demand_signal(df, i)
            signals.append(signal)
        return signals

    def market_structure_signal(self, df: pd.DataFrame) -> List[float]:
        """Generate market structure signals"""
        signals = []
        for i in range(len(df)):
            signal = self.price_action.get_market_structure_signal(df, i)
            signals.append(signal)
        return signals

    def volume_spike_signal(self, df: pd.DataFrame) -> List[float]:
        """
        ORIGINAL RULE: Volume spike signals for breakout confirmation
        """
        signals = []
        for i in range(len(df)):
            signal = self.price_action.get_volume_spike_signal(df, i)
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

    def order_flow_signal(self, df: pd.DataFrame) -> List[float]:
        """Generate order flow imbalance signals"""
        signals = []
        for i in range(len(df)):
            signal = self.price_action.get_order_flow_signal(df, i)
            signals.append(signal)
        return signals
