import pandas as pd
from deepseek.config import Config
from deepseek.data_loader import DataLoader
from deepseek.indicators import Indicators
from deepseek.rule_engine import RuleEngine
from deepseek.rule_scorer import RuleScorer
from deepseek.portfolio_manager import PortfolioManager
from util import file
from fire import Fire


class QuantitativeTradingSystem:
    def __init__(self, df):
        self.config = Config()
        self.data_loader = DataLoader(df)
        self.indicators = Indicators(self.config)
        self.rule_engine = RuleEngine(self.config)
        self.rule_scorer = RuleScorer(self.config, self.rule_engine.get_rules())
        self.portfolio_manager = PortfolioManager(self.config)

        # Process data
        self.prepare_data()

    def analyze_signal_quality(self, results_df: pd.DataFrame):
        """Analyze how often signals are profitable"""
        profitable_buys = 0
        profitable_sells = 0
        total_buys = 0
        total_sells = 0

        for i in range(1, len(results_df)):
            current = results_df.iloc[i]
            prev = results_df.iloc[i - 1]

            if prev["decision"] == "BUY":
                total_buys += 1
                if current["close"] > prev["close"]:
                    profitable_buys += 1

            elif prev["decision"] == "SELL":
                total_sells += 1
                if current["close"] < prev["close"]:
                    profitable_sells += 1

        buy_success_rate = profitable_buys / total_buys if total_buys > 0 else 0
        sell_success_rate = profitable_sells / total_sells if total_sells > 0 else 0

        print("\n=== ANALYZE RESULTS ===")
        print(f"-> Buy Signal Success Rate: {buy_success_rate:.1%}")
        print(f"-> Sell Signal Success Rate: {sell_success_rate:.1%}")
        print(f"-> Overall Signal Quality: {(buy_success_rate + sell_success_rate)/2:.1%}\n")

    def prepare_data(self):
        """Prepare all indicator data"""
        print(
            f"\n=== AVAILABLE RULES ===\n-> {", ".join(self.rule_engine.get_rules())}"
        )
        df = self.data_loader.get_data()
        df_with_indicators = self.indicators.calculate_all_indicators(df)
        df_with_signals = self.rule_engine.generate_all_signals(df_with_indicators)
        self.data = df_with_signals

    def run_backtest(self, strict: bool = False) -> pd.DataFrame:
        """Run the complete adaptive trading system"""
        results = []

        for i in range(self.config.WINDOW_LOOKBACK, len(self.data)):
            current_data = self.data.iloc[i]

            # SIMPLIFIED: Use the RuleEngine to get all signals
            current_signals = self.rule_engine.get_current_signals_dict(current_data)

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
                    weights=weights,
                    df=self.data,
                    current_index=i,
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
                "signals": current_signals.copy(),
                "weights": weights.copy(),
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
        self.strict = True if strict or strict == "True" else False

    def run(self):
        # Load and process data
        df = file.get_source(self.input)
        trading_system = QuantitativeTradingSystem(df)
        results = trading_system.run_backtest(strict=self.strict)
        trading_system.update_decision(results)

        # Display final results
        print("\n=== TRADING SYSTEM RESULTS ===")
        print(f"-> Strict mode: {self.strict}")
        print(f"-> Total periods: {len(results)}")
        print(f"-> Buy signals: {len(results[results['decision'] == 'BUY'])}")
        print(f"-> Sell signals: {len(results[results['decision'] == 'SELL'])}")
        print(f"-> Hold signals: {len(results[results['decision'] == 'HOLD'])}")

        # Show latest weights and signals
        latest = results.iloc[-1]
        latest_weights = latest["weights"]
        print(f"\n=== LATEST SIGNALS (DATE: {latest['date']}) ===")
        print(
            f"-> Rule Weights - RSI: {" | ".join([f"{i}={latest_weights[i]:.3f}" for i in latest_weights])}"
        )
        print(
            f"-> Composite Signal: {latest['composite_signal']:.3f} -> {latest['decision']}"
        )

        trading_system.analyze_signal_quality(results)

        file.write_dataframe(trading_system.data, self.output)


# Example usage
if __name__ == "__main__":
    Fire(Quant_DeepSeek_CLI)
