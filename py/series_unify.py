import ta
import ta.momentum
import ta.trend
import file
import pandas as pd
import json
import os
import datetime
import re


def get_unify_config() -> dict:
    """
    Load the unify configuration from the JSON file.
    """
    config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "unify.json"
    )
    with open(config_path, "r") as json_file:
        return json.load(json_file)


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
    frame[f"{prefix}_next_type"] = frame[f"{prefix}_type"].shift(-1)

    return frame


def get_all_dataframes() -> list[pd.DataFrame]:
    """
    Load and process all dataframes based on the unify configuration.

    Returns:
        list[pd.DataFrame]: List of processed DataFrames.
    """
    unify_config = get_unify_config()
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


def main():
    """
    Main function to unify and process dataframes, then save the result to a CSV file.
    """
    dataframes = get_all_dataframes()
    max_df, small_dataframes = split_to_max_and_small(dataframes)

    print(max_df.head())
    print("Small DataFrames count:", len(small_dataframes))

    # Join smaller DataFrames to the largest one
    for small_df in small_dataframes:
        max_df = max_df.join(small_df, on="timestamp")

    # Drop rows with missing values
    max_df.dropna(inplace=True)

    # Save the final DataFrame to a CSV file
    output_path = "ignore/stock/finalize_copilot.csv"
    file.write(output_path, max_df.to_csv())


if __name__ == "__main__":
    main()
