import pandas as pd
import numpy as np
from config import Config


class PortfolioManager:
    def __init__(self, config):
        self.config = config
        self.positions = []
        self.cash = config.INITIAL_CAPITAL
        self.portfolio_value = config.INITIAL_CAPITAL

    def calculate_composite_signal(self, signals, weights):
        """Calculate weighted composite signal"""
        composite = (
            signals.get("rsi", 0) * weights.get("rsi", 0)
            + signals.get("ma", 0) * weights.get("ma", 0)
            + signals.get("bb", 0) * weights.get("bb", 0)
        )
        return composite

    def generate_trading_decision(self, composite_signal, threshold=0.1):
        """Generate trading decision based on composite signal"""
        if composite_signal > threshold:
            return "BUY", composite_signal
        elif composite_signal < -threshold:
            return "SELL", composite_signal
        else:
            return "HOLD", composite_signal

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
