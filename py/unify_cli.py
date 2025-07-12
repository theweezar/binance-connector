import ta
import ta.momentum
import ta.trend
import file
import pandas as pd
import datetime
import re
import fire
import processor
from sklearn.metrics import accuracy_score


def convert_date_to_timestamp(date_str: str) -> str:
    """
    Convert a date string in the format MM/DD/YYYY to a Unix timestamp.
    """

    if re.search(r"\d+\/", date_str) is not None:
        return str(int(datetime.datetime.strptime(date_str, "%m/%d/%Y").timestamp()))

    if re.search(r"\d+\-", date_str) is not None:
        return str(int(datetime.datetime.strptime(date_str, "%Y-%m-%d").timestamp()))


def process_dataframe(dataframe: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """
    Processes the input DataFrame by calculating various technical indicators.

    Args:
        dataframe (pd.DataFrame): The input DataFrame containing market data.
        prefix (str): Prefix for column names.

    Returns:
        pd.DataFrame: The processed DataFrame with additional columns for technical indicators.
    """
    frame = dataframe.copy()

    # Extract relevant columns
    _open = frame[f"{prefix}_open"]
    close = frame[f"{prefix}_close"]
    high = frame[f"{prefix}_high"]
    low = frame[f"{prefix}_low"]

    # Calculate indicators
    frame[f"{prefix}_price_change"] = close.pct_change()
    frame[f"{prefix}_volatility"] = close.rolling(10).std()

    frame[f"{prefix}_rsi_6"] = ta.momentum.rsi(close, 6)
    frame[f"{prefix}_rsi_7"] = ta.momentum.rsi(close, 7)
    frame[f"{prefix}_rsi_9"] = ta.momentum.rsi(close, 9)
    frame[f"{prefix}_rsi_12"] = ta.momentum.rsi(close, 12)
    frame[f"{prefix}_rsi_14"] = ta.momentum.rsi(close, 14)
    frame[f"{prefix}_rsi_30"] = ta.momentum.rsi(close, 30)

    frame[f"{prefix}_sma_20"] = ta.trend.sma_indicator(close, 20)
    frame[f"{prefix}_sma_50"] = ta.trend.sma_indicator(close, 50)

    ema_34 = ta.trend.ema_indicator(close, 34)
    ema_89 = ta.trend.ema_indicator(close, 89)
    frame[f"{prefix}_ema_34"] = ema_34
    frame[f"{prefix}_ema_89"] = ema_89
    frame[f"{prefix}_ema_trend"] = ema_34 - ema_89

    ema_12 = ta.trend.ema_indicator(close, 12)
    ema_26 = ta.trend.ema_indicator(close, 26)
    macd = ema_12 - ema_26
    frame[f"{prefix}_macd"] = macd
    frame[f"{prefix}_macd_signal"] = ta.trend.ema_indicator(macd, 9)

    frame[f"{prefix}_adx_14"] = ta.trend.ADXIndicator(high, low, close).adx()

    # Add type and next_type columns
    frame[f"{prefix}_type"] = (close >= _open).astype(int).astype(str)
    # frame[f"{prefix}_next_type"] = frame[f"{prefix}_type"].shift(-1)

    return frame


def get_all_dataframes(config_path: str) -> list[pd.DataFrame]:
    """
    Load and process all dataframes based on the unify configuration.

    Returns:
        list[pd.DataFrame]: List of processed DataFrames.
    """
    print(f"Loading unify config from {config_path}")
    unify_config = file.require(config_path)
    dataframes = []

    for conf in unify_config:
        src = file.get_source(conf["path"])
        df = src["dataframe"]

        # Rename columns based on configuration
        rename_config = conf["rename"]["columns"]
        prefix = conf["rename"]["prefix"]
        rename_map = {
            col_conf["from"]: col_conf["to"].format(prefix=prefix)
            for col_conf in rename_config
        }
        # Collect original column names about to be renamed
        rename_columns = [col_conf["from"] for col_conf in rename_config]

        # Collect all column names
        df_columns = df.columns.tolist()

        # Remove columns that are not in rename_columns
        drop_columns = [col for col in df_columns if col not in rename_columns]
        df.drop(columns=drop_columns, inplace=True)
        print(f"Drop columns: {drop_columns} in {conf['path']}")

        df.rename(columns=rename_map, inplace=True)
        df.replace({r",": ""}, inplace=True, regex=True)

        # Apply type conversions
        for col_conf in rename_config:
            col_name = col_conf["to"].format(prefix=prefix)
            if "type" in col_conf:
                df[col_name] = df[col_name].astype(col_conf["type"])

        # Add timestamp column and sort by it
        df["timestamp"] = df[f"{prefix}_date"].apply(convert_date_to_timestamp)
        df.sort_values(by="timestamp", ascending=True, inplace=True)
        df.set_index("timestamp", inplace=True)

        # Process the DataFrame
        processed_df = process_dataframe(df, prefix)
        dataframes.append(processed_df)

    return dataframes


def split_to_max_and_small(
    dataframes: list[pd.DataFrame],
) -> tuple[pd.DataFrame, list[pd.DataFrame]]:
    """
    Split the list of DataFrames into the largest DataFrame and smaller ones.

    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames.

    Returns:
        tuple[pd.DataFrame, list[pd.DataFrame]]: The largest DataFrame and a list of smaller DataFrames.
    """
    max_df = pd.DataFrame()
    small_dataframes = []

    for df in dataframes:
        if max_df.empty or len(df) > len(max_df):
            if not max_df.empty:
                small_dataframes.append(max_df)
            max_df = df
        else:
            small_dataframes.append(df)

    return max_df, small_dataframes


def select_df_range(df: pd.DataFrame, range: str) -> pd.DataFrame:
    """
    Select a range of rows from the DataFrame based on start and end timestamps.

    Args:
        df (pd.DataFrame): The input DataFrame.
        range (str): The range of rows to select, in the format "start:end".

    Returns:
        pd.DataFrame: The selected range of rows from the DataFrame.
    """

    range_split = range.strip().split(":")
    start = (
        int(range_split[0]) if len(range_split) > 0 and range_split[0] != "" else None
    )
    end = int(range_split[1]) if len(range_split) > 1 and range_split[1] != "" else None

    if start and end:
        return df[start:end]
    elif start:
        return df[start:]
    elif end:
        return df[:end]
    else:
        return df


class Unify_CLI(object):
    """
    Class to handle the unification of DataFrames based on a configuration file.
    """

    def unify(
        self,
        config: str = "config/unify.json",
        output: str = "ignore/stock/unified.csv",
        select: str = "",
    ):
        """
        Main function to unify and process dataframes, then save the result to a CSV file.

        Args:
            output (str): The path to the output unified CSV file.
        """
        dataframes = get_all_dataframes(config)
        max_df, small_dataframes = split_to_max_and_small(dataframes)

        # Join smaller DataFrames to the largest one
        for small_df in small_dataframes:
            max_df = max_df.join(small_df, on="timestamp")

        # Drop rows with missing values
        max_df.dropna(inplace=True)

        max_df = select_df_range(max_df, select)
        # Save the final DataFrame to a CSV file
        file.write(output, max_df.to_csv(lineterminator="\n"))
        print(f"Unified data saved to {output}")

    def train(self, source: str = "", export: str = "ignore/unified_model.pkl"):
        """
        Process the source data using a processor module.

        Args:
            source (str): The path to the source data.
        """
        _source = file.get_source(source)

        print(f"Start processing data for {_source['filepath']}")

        x, y = processor.preprocess_unified_data(_source["dataframe"])

        import py.model.logistic_reg_model as logistic_reg_model

        print(f"Start training unified data for {_source['filepath']}")
        _model = logistic_reg_model.train(x.values, y.values)

        file.export_py_object(export, _model)

    def predict(self, source, model):
        _source = file.get_source(source)

        print(f"Start processing data for {_source['filepath']}")

        x, y = processor.preprocess_unified_data(_source["dataframe"])
        _model = file.load(model)
        y_pred = _model.predict(x.values)

        print(f"Prediction:\n{y_pred}")
        print(f"Actual:\n{y.values}")

        accuracy = accuracy_score(y.values, y_pred)

        print(f"Model Accuracy: {accuracy:.2f}")


if __name__ == "__main__":
    unify_cli = Unify_CLI()
    fire.Fire(unify_cli)
