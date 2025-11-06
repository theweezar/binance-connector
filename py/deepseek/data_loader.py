import pandas as pd


class DataLoader:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.prepare_data()

    def prepare_data(self):
        """Ensure data is sorted and has returns calculated"""
        self.df = self.df.sort_values("timestamp").reset_index(drop=True)
        self.df["returns"] = self.df["close"].pct_change()

    def get_data(self):
        return self.df

    def get_subset(self, start_idx, end_idx):
        return self.df.iloc[start_idx:end_idx].copy()
