import fire
import numpy as np
from util import file
from processors import indicator


class Processor_CLI(object):
    """
    Command Line Interface for processing data using indicators.
    """

    def process(self, source: str, output: str):
        """
        Process the source data using a processor module.

        Args:
            source (str): The path to the source data.
            output (str): The path to the output data.
        """
        _source = file.get_source(source)

        print(f"Start processing data for {_source['filepath']}")

        df = indicator.apply(_source["dataframe"])

        file.write_dataframe(df, output)

    def polyfit(self, source: str, output: str, steps: int = 6):
        """
        Apply polynomial fitting to the source data.

        Args:
            source (str): The path to the source data.
            output (str): The path to the output data.
            steps (int): The number of steps for the polynomial fitting.
        """
        _source = file.get_source(source)
        df = _source["dataframe"]
        length = len(df)
        cp_df = df.copy()
        cp_df["trend"] = "-"

        for i in range(length, -1, -steps):
            if i < steps:
                continue
            sub_df = cp_df[i - steps : i]
            nd_price = np.array(sub_df["open"])
            nd_timestamp = np.array(sub_df["timestamp"])
            m, b = np.polyfit(nd_timestamp, nd_price, 1)
            trendline = m * nd_timestamp + b
            cp_df.loc[sub_df.index, "trend"] = trendline

        file.write_dataframe(cp_df, output)


if __name__ == "__main__":
    processor_cli = Processor_CLI()
    fire.Fire(processor_cli)
