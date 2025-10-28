import pandas as pd
import numpy as np
from config import Config
from data_loader import DataLoader
from indicators import Indicators
from rule_engine import RuleEngine
from rule_scorer import RuleScorer
from portfolio_manager import PortfolioManager


class QuantitativeTradingSystem:
    def __init__(self, df):
        self.config = Config()
        self.data_loader = DataLoader(df)
        self.indicators = Indicators(self.config)
        self.rule_engine = RuleEngine(self.config)
        self.rule_scorer = RuleScorer(self.config)
        self.portfolio_manager = PortfolioManager(self.config)

        # Process data
        self.prepare_data()

    def prepare_data(self):
        """Prepare all indicator data"""
        df = self.data_loader.get_data()
        df_with_indicators = self.indicators.calculate_all_indicators(df)
        df_with_signals = self.rule_engine.generate_all_signals(df_with_indicators)
        self.data = df_with_signals

    def run_backtest(self):
        """Run the complete adaptive trading system"""
        results = []

        for i in range(self.config.LOOKBACK_WINDOW, len(self.data)):
            current_data = self.data.iloc[i]
            current_signals = {
                "rsi": current_data["signal_rsi"],
                "ma": current_data["signal_ma"],
                "bb": current_data["signal_bb"],
            }

            # Get dynamic rule weights
            weights = self.rule_scorer.get_current_weights(self.data, i)

            # Calculate composite signal
            composite_signal = self.portfolio_manager.calculate_composite_signal(
                current_signals, weights
            )

            # Generate trading decision
            decision = self.portfolio_manager.generate_trading_decision(
                composite_signal
            )

            # Update portfolio
            portfolio_snapshot = self.portfolio_manager.update_portfolio(
                decision, current_data["close"], current_data["start_time"]
            )

            # Store results
            result = {
                "date": current_data["start_time"],
                "close": current_data["close"],
                "signals": current_signals,
                "weights": weights,
                "composite_signal": composite_signal,
                "decision": decision[0],
                "signal_strength": decision[1],
            }
            results.append(result)

            # Print current state (optional)
            if i % 30 == 0:  # Print every 30 days
                print(f"Date: {current_data['start_time']}")
                print(
                    f"  Signals: RSI={current_signals['rsi']}, MA={current_signals['ma']}, BB={current_signals['bb']}"
                )
                print(
                    f"  Weights: RSI={weights['rsi']:.2f}, MA={weights['ma']:.2f}, BB={weights['bb']:.2f}"
                )
                print(f"  Composite: {composite_signal:.3f} -> {decision[0]}")
                print("-" * 50)

        return pd.DataFrame(results)


# Example usage
if __name__ == "__main__":
    # Assuming you have your dataframe loaded as `df`
    # Example structure: columns = ['start_time', 'end_time', 'high', 'low', 'open', 'close', 'volume']

    # Create and run the system
    trading_system = QuantitativeTradingSystem(df)
    results = trading_system.run_backtest()

    # Display final results
    print("\n=== TRADING SYSTEM RESULTS ===")
    print(f"Total periods: {len(results)}")
    print(f"Buy signals: {len(results[results['decision'] == 'BUY'])}")
    print(f"Sell signals: {len(results[results['decision'] == 'SELL'])}")
    print(f"Hold signals: {len(results[results['decision'] == 'HOLD'])}")

    # Show latest weights and signals
    latest = results.iloc[-1]
    print(f"\nLatest signals (Date: {latest['date']}):")
    print(
        f"  Rule Weights - RSI: {latest['weights']['rsi']:.3f}, MA: {latest['weights']['ma']:.3f}, BB: {latest['weights']['bb']:.3f}"
    )
    print(
        f"  Composite Signal: {latest['composite_signal']:.3f} -> {latest['decision']}"
    )
    print(results[["date", "composite_signal", "decision"]].tail(10))
