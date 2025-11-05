import numpy as np


class RuleScorer:
    def __init__(self, config):
        self.config = config

    def calculate_rule_performance(self, df_subset):
        """Calculate cumulative returns for each rule over the evaluation period"""
        performance = {}

        for rule in ["rsi", "ma", "bb"]:
            signal_col = f"signal_{rule}"
            returns = df_subset["returns"].iloc[1:].values  # Skip first NaN
            signals = (
                df_subset[signal_col].iloc[1:-1].values
            )  # Align with next day's return

            # Calculate rule returns (signal * next_day_return)
            rule_returns = signals * returns[1 : len(signals) + 1]
            cumulative_return = np.prod(1 + rule_returns) - 1

            performance[rule] = cumulative_return

        return performance

    def calculate_rule_weights(self, performance_dict):
        """Calculate exponential weights for each rule based on performance"""
        scores = {}

        for rule, perf in performance_dict.items():
            # Exponential scoring
            scores[rule] = np.exp(perf * self.config.SENSITIVITY_FACTOR)

        # Normalize to sum to 1
        total_score = sum(scores.values())
        weights = {rule: score / total_score for rule, score in scores.items()}

        return weights

    def get_current_weights(self, full_data, current_index):
        """Calculate weights for current point based on lookback window"""
        if current_index < self.config.LOOKBACK_WINDOW:
            # Not enough data, return equal weights
            return {"rsi": 0.33, "ma": 0.33, "bb": 0.34}

        start_idx = current_index - self.config.LOOKBACK_WINDOW
        end_idx = current_index

        evaluation_data = full_data.iloc[start_idx:end_idx].copy()
        performance = self.calculate_rule_performance(evaluation_data)
        weights = self.calculate_rule_weights(performance)

        return weights
