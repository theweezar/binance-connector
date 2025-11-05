import pandas as pd
from deepseek.config import Config, Config15M
from deepseek.data_loader import DataLoader
from deepseek.indicators import Indicators
from deepseek.rule_engine import RuleEngine
from deepseek.rule_scorer import RuleScorer
from deepseek.portfolio_manager import PortfolioManager
from util import file
from fire import Fire


class QuantitativeTradingSystem:
    def __init__(self, df):
        self.config = Config15M()
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

    def run_backtest(self, strict: bool = False):
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
            if not strict:
                decision = self.portfolio_manager.generate_trading_decision(
                    composite_signal=composite_signal,
                    buy_threshold=0.3,
                    sell_threshold=-0.3,
                )

            if strict:
                decision = self.portfolio_manager.strict_generate_trading_decision(
                    composite_signal=composite_signal,
                    current_data=self.data,
                    current_index=i,
                )

            # Store results
            result = {
                "timestamp": current_data["timestamp"],
                "date": current_data["start"],
                "close": current_data["close"],
                "signals": current_signals,
                "weights": weights,
                "composite_signal": composite_signal,
                "decision": decision[0],
                "signal_strength": decision[1],
            }
            results.append(result)

        return pd.DataFrame(results)

    def update_decision(self, results: pd.DataFrame):
        for i in range(len(results)):
            result = results.iloc[i]
            idx = self.data[self.data["timestamp"] == result["timestamp"]].index
            self.data.loc[idx, "entry_signal"] = result["decision"]


class Quant_DeepSeek_CLI:
    def __init__(self, input: str, output: str, strict: bool = False):
        self.input = input
        self.output = output
        self.strict = strict

    def run(self):
        # Load and process data
        df = file.get_source(self.input)
        trading_system = QuantitativeTradingSystem(df)
        results = trading_system.run_backtest(strict=self.strict)
        trading_system.update_decision(results)

        # Display final results
        print("\n=== TRADING SYSTEM RESULTS ===")
        print(f"Strict mode: {self.strict}")
        print(f"Total periods: {len(results)}")
        print(f"Buy signals: {len(results[results['decision'] == 'BUY'])}")
        print(f"Sell signals: {len(results[results['decision'] == 'SELL'])}")
        print(f"Hold signals: {len(results[results['decision'] == 'HOLD'])}")

        # Show latest weights and signals
        latest = results.iloc[-1]
        print(f"\nLatest signals (Date: {latest['date']}):")
        print(
            f"- Rule Weights - RSI: {latest['weights']['rsi']:.3f}, MA: {latest['weights']['ma']:.3f}, BB: {latest['weights']['bb']:.3f}"
        )
        print(
            f"- Composite Signal: {latest['composite_signal']:.3f} -> {latest['decision']}\n"
        )

        file.write_dataframe(trading_system.data, self.output)


# Example usage
if __name__ == "__main__":
    Fire(Quant_DeepSeek_CLI)
