from datetime import datetime


class SignalFilter:
    def __init__(self, config):
        self.config = config

    def volume_confirmation(self, df, current_index, volume_threshold=1.2):
        """Require above-average volume for signals"""
        if current_index < 20:
            return True

        current_volume = df["volume"].iloc[current_index]
        avg_volume = df["volume"].iloc[current_index - 20 : current_index].mean()

        return current_volume > (avg_volume * volume_threshold)

    def volatility_filter(self, df, current_index, max_volatility=0.02):
        """Filter signals during high volatility periods"""
        if current_index < 10:
            return True

        recent_volatility = (
            df["close"].iloc[current_index - 10 : current_index].pct_change().std()
        )
        return recent_volatility <= max_volatility

    def time_based_filter(self, current_timestamp, avoid_periods=None):
        """Avoid trading during certain times"""
        if avoid_periods is None:
            avoid_periods = ["00:00", "06:00"]  # Low liquidity times
        current_time = datetime.fromtimestamp(current_timestamp / 1000)
        current_hour_min = current_time.strftime("%H:%M")
        return current_hour_min not in avoid_periods

    def consecutive_signal_filter(self, recent_signals, current_signal, min_changes=2):
        """Require signal to persist for multiple periods"""
        if len(recent_signals) < min_changes:
            return True

        # Check if we've had consistent signals
        recent_consistent = all(
            s == current_signal for s in recent_signals[-min_changes + 1 :]
        )
        return recent_consistent


class PortfolioManager:
    def __init__(self, config):
        self.config = config
        self.positions = []
        self.cash = config.INITIAL_CAPITAL
        self.portfolio_value = config.INITIAL_CAPITAL
        self.signal_filter = SignalFilter(config)
        self.consecutive_signals = []

    def update_portfolio(self, decision, price, date):
        """Update portfolio based on trading decision"""
        # Simple implementation - in practice you'd add position sizing, risk management, etc.
        decision_type, signal_strength = decision

        # For demo purposes, just track decisions
        portfolio_snapshot = {
            "date": date,
            "decision": decision_type,
            "signal_strength": signal_strength,
            "portfolio_value": self.portfolio_value,
            "cash": self.cash,
        }

        self.positions.append(portfolio_snapshot)
        return portfolio_snapshot

    def calculate_composite_signal(self, signals, weights):
        """Calculate weighted composite signal"""
        composite = (
            signals.get("rsi", 0) * weights.get("rsi", 0)
            + signals.get("ma", 0) * weights.get("ma", 0)
            + signals.get("bb", 0) * weights.get("bb", 0)
        )
        return composite

    def generate_trading_decision(
        self, composite_signal, buy_threshold=0.3, sell_threshold=-0.3
    ):
        if composite_signal > buy_threshold:
            return "BUY", composite_signal
        elif composite_signal < sell_threshold:
            return "SELL", composite_signal
        else:
            return "HOLD", composite_signal

    def update_signal_history(self, composite_signal):
        """Keep track of recent signals for confirmation"""
        self.consecutive_signals.append(composite_signal)
        if len(self.consecutive_signals) > 5:  # Keep last 5 periods
            self.consecutive_signals.pop(0)

    def strict_generate_trading_decision(
        self,
        composite_signal,
        current_data,
        current_index,
        strict_threshold=0.4,
        moderate_threshold=0.25,
    ):
        """Multi-threshold system with filters"""

        # STRICT FILTERS - Only trade if all pass
        volume_ok = (
            True  # self.signal_filter.volume_confirmation(current_data, current_index)
        )
        volatility_ok = self.signal_filter.volatility_filter(
            current_data, current_index
        )
        time_ok = self.signal_filter.time_based_filter(
            current_data["timestamp"].iloc[current_index]
        )

        self.update_signal_history(composite_signal=composite_signal)

        if not (volume_ok and volatility_ok and time_ok):
            return "HOLD", composite_signal

        # MULTI-LEVEL THRESHOLDS
        if composite_signal > strict_threshold:
            # Strong buy - require confirmation
            if len(self.consecutive_signals) >= 2:
                if all(s > moderate_threshold for s in self.consecutive_signals[-2:]):
                    return "BUY", composite_signal

        elif composite_signal < -strict_threshold:
            # Strong sell - require confirmation
            if len(self.consecutive_signals) >= 2:
                if all(s < -moderate_threshold for s in self.consecutive_signals[-2:]):
                    return "SELL", composite_signal

        elif abs(composite_signal) > moderate_threshold:
            # Moderate signal - wait for confirmation
            pass

        return "HOLD", composite_signal
