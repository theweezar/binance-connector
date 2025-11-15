import numpy as np
import pandas as pd
from typing import Dict


class RuleScorer:
    def __init__(self, config, rules: dict[str]):
        self.config = config
        self.rules = rules

    def calculate_rule_performance(self, df_subset: pd.DataFrame) -> Dict[str, float]:
        """Calculate cumulative returns for each rule including new ones"""
        performance = {}

        for rule in self.rules:
            signal_col = f"signal_{rule}"
            returns = df_subset["returns"].iloc[1:].values
            signals = df_subset[signal_col].iloc[1:-1].values

            # Handle cases where arrays might not align
            min_length = min(len(signals), len(returns) - 1)
            if min_length == 0:
                performance[rule] = 0.0
                continue

            signals = signals[:min_length]
            aligned_returns = returns[1 : 1 + min_length]

            # Handle fractional signals
            rule_returns = signals * aligned_returns
            cumulative_return = np.prod(1 + rule_returns) - 1

            performance[rule] = cumulative_return

        return performance

    def calculate_rule_weights(self, performance_dict: dict) -> Dict[str, float]:
        """Calculate exponential weights for each rule based on performance"""
        scores = {}

        for rule, perf in performance_dict.items():
            # Exponential scoring with smoothing for negative returns
            # Cap losses at -50% for scoring
            adjusted_perf = max(perf, -0.5)
            scores[rule] = np.exp(adjusted_perf * self.config.SENSITIVITY_FACTOR)

        # Normalize to sum to 1
        total_score = sum(scores.values())
        weights = {rule: score / total_score for rule, score in scores.items()}

        return weights

    def get_current_weights(
        self, full_data: pd.DataFrame, current_index
    ) -> Dict[str, float]:
        """Calculate weights for current point based on lookback window"""
        if current_index < self.config.WINDOW_LOOKBACK:
            # Equal weights initially
            equal_weight = 1.0 / len(self.rules)
            return {rule: equal_weight for rule in self.rules}

        start_idx = current_index - self.config.WINDOW_LOOKBACK
        end_idx = current_index

        evaluation_data = full_data.iloc[start_idx:end_idx].copy()
        performance = self.calculate_rule_performance(evaluation_data)
        weights = self.calculate_rule_weights(performance)

        return weights
