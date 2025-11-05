import pandas
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def apply_grok3_solution(dataframe: pandas.DataFrame):
    """
    Applies the Grok3 scaling solution to the input DataFrame.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame containing market data.

    Returns:
        pandas.DataFrame: The scaled DataFrame with selected features.
    """
    print("Using Grok3 solution")
    standard_scaler = StandardScaler()
    minmax_scaler = MinMaxScaler()
    data = dataframe.copy()

    standard_x_features = data[
        [
            "close",
            "vol",
            "ema_34",
            "ema_89",
        ]
    ]
    standard_x_features = pandas.DataFrame(
        standard_scaler.fit_transform(standard_x_features.values),
        columns=standard_x_features.columns.values,
    )

    minmax_x_features = data[
        [
            "ema_trend",
            "rsi_6",
            "rsi_9",
            "macd",
            "macd_signal",
            "adx_14",
        ]
    ]
    minmax_x_features = pandas.DataFrame(
        minmax_scaler.fit_transform(minmax_x_features.values),
        columns=minmax_x_features.columns.values,
    )

    X_scaled = standard_x_features.join(minmax_x_features)

    return X_scaled


def apply_chatgpt_solution(dataframe: pandas.DataFrame):
    """
    Applies the ChatGPT scaling solution to the input DataFrame.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame containing market data.

    Returns:
        pandas.DataFrame: The scaled DataFrame with selected features.
    """
    print("Using ChatGPT solution")
    data = dataframe.copy()

    # Raw X values
    x_features = data[
        [
            # "close",
            # "vol",
            "ema_trend",
            "rsi_6",
            "rsi_9",
            "ema_34",
            "ema_89",
            "macd",
            "macd_signal",
            "adx_14",
        ]
    ]

    # Initialize StandardScaler
    scaler = StandardScaler()

    # Scale the dataset
    X_scaled = scaler.fit_transform(x_features.values)

    return pandas.DataFrame(X_scaled)


def process_data(
    dataframe: pandas.DataFrame, dropna: bool = False
) -> tuple[pandas.DataFrame, pandas.DataFrame, str]:
    """
    Preprocesses the data for model training.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        dropna (bool): Whether to drop NaN values from the DataFrame.

    Returns:
        tuple: A tuple containing the scaled features (X), target (y), and symbol.
    """
    data = dataframe.copy()
    symbol = data["symbol"][0]

    if dropna is True:
        print("Dropping NaN values")
        data.dropna(inplace=True)

    # X_scaled = apply_grok3_solution(data)
    X_scaled = apply_chatgpt_solution(data)

    # Binary classification -> Up/Down -> raw y values
    y_target = (data["next_type"] == "U").astype(int)

    return X_scaled, y_target, symbol


def preprocess_unified_data(
    dataframe: pandas.DataFrame,
) -> tuple[pandas.DataFrame, pandas.DataFrame]:
    """
    Preprocesses the unified DataFrame by scaling and selecting features.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.

    Returns:
        tuple: A tuple containing the scaled features (x), target (y).
    """

    standard_cols = []
    minmax_cols = []
    drop_cols = ["btc_type"]

    standard_keywords = [
        # "open",
        # "high",
        # "low",
        # "close",
        # "price_change",
        # "volatility",
        "sma",
        # "ema_34",
        # "ema_89",
        # "macd",
        # "macd_signal",
        "type",
    ]

    minmax_keywords = [
        "rsi",
        "adx",
        "ema_trend",
    ]

    for col in dataframe.columns:
        if any(keyword in col for keyword in standard_keywords):
            standard_cols.append(col)
        elif any(keyword in col for keyword in minmax_keywords):
            minmax_cols.append(col)
        else:
            drop_cols.append(col)

    # Initialize scalers
    standard_scaler = StandardScaler()
    minmax_scaler = MinMaxScaler()

    # Fit and transform
    df_scaled = dataframe.copy()

    if standard_cols:
        df_scaled[standard_cols] = standard_scaler.fit_transform(
            dataframe[standard_cols]
        )

    if minmax_cols:
        df_scaled[minmax_cols] = minmax_scaler.fit_transform(dataframe[minmax_cols])

    print(f"Dropping columns: {", ".join(drop_cols)}\n")
    df_scaled.drop(columns=drop_cols, inplace=True)
    print(f"Selecting columns: {", ".join(df_scaled.columns.to_list())}\n")
    y_target = dataframe["btc_type"]

    return df_scaled, y_target
