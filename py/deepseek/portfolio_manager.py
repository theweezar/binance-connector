import pandas as pd
from datetime import datetime


class SignalFilter:
    def __init__(self, config):
        self.config = config

    def volume_confirmation(
        self,
        df: pd.DataFrame,
        current_index: int,
        volume_threshold: float = 1.2,
        periods: int = 20,
    ):
        """Require above-average volume for signals"""
        if current_index < periods:
            return True

        current_volume = df["volume"].iloc[current_index]
        avg_volume = df["volume"].iloc[current_index - periods : current_index].mean()

        return current_volume > (avg_volume * volume_threshold)

    def volatility_filter(
        self,
        df: pd.DataFrame,
        current_index: int,
        max_volatility: float = 0.02,
        periods: int = 10,
    ):
        """Filter signals during high volatility periods"""
        if current_index < periods:
            return True

        recent_volatility = (
            df["close"].iloc[current_index - periods : current_index].pct_change().std()
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

        # Threshold parameters
        self.base_threshold = config.BASE_THRESHOLD
        self.min_threshold = config.MIN_THRESHOLD
        self.max_threshold = config.MAX_THRESHOLD
        self.method = config.THRESHOLD_METHOD
        self.recent_composite_signals = []

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

    def calculate_composite_signal(self, signals: dict, weights: dict):
        """
        Calculate weighted composite signal dynamically for all rules

        Args:
            signals: dict of {rule_name: signal_value}
            weights: dict of {rule_name: weight_value}

        Returns:
            Composite signal as weighted sum of all rule signals
        """
        composite = 0.0

        # Loop through all rules that have both signals and weights
        for rule_name, signal_value in signals.items():
            weight = weights.get(rule_name, 0)
            composite += signal_value * weight

        return composite

    def count_active_rules(self, weights: dict, min_weight=0.05):
        """Count rules with significant weight"""
        return sum(1 for weight in weights.values() if weight >= min_weight)

    def calculate_market_volatility(self, df: pd.DataFrame, current_index, lookback=10):
        """Calculate recent price volatility"""
        if current_index < lookback:
            return 0

        recent_prices = df["close"].iloc[current_index - lookback : current_index]
        returns = recent_prices.pct_change().dropna()
        return returns.std()

    def generate_trading_decision(
        self, composite_signal, weights, df: pd.DataFrame, current_index
    ):
        """Generate trading decision with adaptive threshold"""
        if self.method == "fixed":
            threshold = self.base_threshold

        elif self.method == "adaptive":
            # Adjust based on number of active rules
            active_rules = self.count_active_rules(
                weights, min_weight=self.config.ADAPTIVE_THRESHOLD
            )
            threshold = self.base_threshold * (
                active_rules / 3.0
            )  # Normalize to original 3 rules
            threshold = max(self.min_threshold, min(self.max_threshold, threshold))

        elif self.method == "volatility":
            # Adjust based on market volatility
            volatility = self.calculate_market_volatility(df, current_index)
            threshold = self.base_threshold * (
                1 + volatility * 10
            )  # Scale volatility effect
            threshold = max(self.min_threshold, min(self.max_threshold, threshold))

        else:
            threshold = self.base_threshold

        # Store for tracking
        self.recent_composite_signals.append(composite_signal)
        if len(self.recent_composite_signals) > 50:
            self.recent_composite_signals.pop(0)

        if composite_signal > threshold:
            return "BUY", composite_signal, threshold
        elif composite_signal < -threshold:
            return "SELL", composite_signal, threshold
        else:
            return "HOLD", composite_signal, threshold

    def update_signal_history(self, composite_signal):
        """Keep track of recent signals for confirmation"""
        self.consecutive_signals.append(composite_signal)
        if len(self.consecutive_signals) > 5:  # Keep last 5 periods
            self.consecutive_signals.pop(0)
