# quantmain.py
import importlib
import pandas as pd
import numpy as np
from fire import Fire
from quantcore import indicator
from util import file

# ---- Config ----
rule_list = ["rule1_trend", "rule2_meanrev", "rule3_breakout", "rule4_liquidity"]


def run_quant(df: pd.DataFrame) -> pd.DataFrame:
    """Main quant processing pipeline"""
    # Apply each rule dynamically
    for rule_name in rule_list:
        module = importlib.import_module(f"quantcore.{rule_name}")
        df = module.apply(df)

    # ---- Bias Scoring ----
    score_cols = [
        f"score_{r}"
        for r in [f.split("_")[0] + "_" + f.split("_")[1] for f in rule_list]
    ]
    signal_cols = [
        f"signal_{r}"
        for r in [f.split("_")[0] + "_" + f.split("_")[1] for f in rule_list]
    ]

    df["bias_rule"] = df[score_cols].idxmax(axis=1)
    df["entry_signal"] = 0
    df['bias_rule_temp'] = df['bias_rule'].where(df['bias_rule'] != df['bias_rule'].shift(), np.nan)
    df['bias_rule'] = df['bias_rule_temp'].ffill()
    df.drop(columns=['bias_rule_temp'], inplace=True)

    for i, rule_name in enumerate(rule_list, start=1):
        signal_col = f"signal_{rule_name}"
        df.loc[df["bias_rule"] == f"score_{rule_name}", "entry_signal"] = df[signal_col]

    return df

# python py/quantchatgpt.py run --input=ignore/XAUT-USDT_15m.csv --output=web/dist/file/XAUT-USDT_15m_quant.csv
class Quant_ChatGPT_CLI:
    def __init__(self, input: str, output: str):
        self.input = input
        self.output = output

    def run(self):
        # Load and process data
        df = file.get_source(self.input)
        df = indicator.add_indicators(df)
        df = run_quant(df)
        file.write_dataframe(df, self.output)


if __name__ == "__main__":
    Fire(Quant_ChatGPT_CLI)
