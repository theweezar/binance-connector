import pandas as pd
from collections import deque


class PriceAction:
    def __init__(self, config):
        self.config = config
        self.support_levels = deque(maxlen=10)  # Keep recent support levels
        self.resistance_levels = deque(maxlen=10)  # Keep recent resistance levels

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
            recent_data, lookback_period=self.config.SUPPORT_RESISTANCE_LOOKBACK
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
            # "rsi_ma": self.rsi_ma_momentum_signal,
            # "price_action": self.price_action_signal,
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
