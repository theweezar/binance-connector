class RuleEngine:
    def __init__(self, config):
        self.config = config

    def momentum_rsi_signal(self, df):
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

    def ma_crossover_signal(self, df):
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

    def bollinger_bands_signal(self, df):
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

    def generate_all_signals(self, df):
        """Generate signals for all rules"""
        df = df.copy()
        df["signal_rsi"] = self.momentum_rsi_signal(df)
        df["signal_ma"] = self.ma_crossover_signal(df)
        df["signal_bb"] = self.bollinger_bands_signal(df)
        return df
