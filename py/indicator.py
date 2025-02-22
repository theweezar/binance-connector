import numpy as np
import pandas
import math


def calc_rsi(prices: pandas.Series, period: int):
    """
    Calculate RSI

    Args:
        prices (Series): Close price series
        period (int): Period

    Returns:
        Series: RSI Series
    """

    # Calc diff = Curr price - Prev price
    diff_prices = prices.diff()

    # Separate gains and losses
    gains = diff_prices.where(diff_prices > 0, 0)
    losses = -diff_prices.where(diff_prices < 0, 0)

    # Calculate the initial average gain and average loss
    avg_gain = gains.rolling(window=period, min_periods=period).mean()
    avg_loss = losses.rolling(window=period, min_periods=period).mean()

    # Calculate smoothed averages for subsequent periods
    for i in range(period, len(prices)):
        avg_gain[i] = ((avg_gain[i - 1] * (period - 1)) + gains[i]) / period
        avg_loss[i] = ((avg_loss[i - 1] * (period - 1)) + losses[i]) / period

    # Calculate Relative Strength (RS)
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    # rsi = rsi.map(lambda val: 50 if math.isnan(val) else val)

    return rsi


def calc_ema(prices: list | pandas.Series, period: int):
    """
    Calculate the Exponential Moving Average (EMA) for a given dataset.

    Args:
        prices (list or pandas.Series): List of price data (closing prices).
        period (int): The number of periods for the EMA.

    Returns:
        pandas.Series: EMA values for the given price data.
    """
    # Convert prices to a pandas Series if it's not already

    this_prices = pandas.Series(prices) if type(prices) is not pandas.Series else prices

    # Calculate EMA using pandas' built-in function
    ema = this_prices.ewm(span=period, adjust=False).mean()

    return ema


def calc_price_if_rsi_reach_to(
    prices: pandas.Series, desired_rsi: float, period: int, price_offset: int
):
    this_prices = prices.copy()
    current_rsi = calc_rsi(this_prices, period)

    length = len(current_rsi)

    if current_rsi[length - 1] >= desired_rsi:
        return this_prices[length - 1]

    this_rsi = current_rsi[length - 1]

    while this_rsi < desired_rsi:
        this_prices[length - 1] = this_prices[length - 1] + price_offset
        rsi_add_offset = calc_rsi(this_prices, period)
        this_rsi = rsi_add_offset[length - 1]

    return this_prices[length - 1]


def calc_price_if_rsi_drop_to(
    prices: pandas.Series, desired_rsi: float, period: int, price_offset: int
):
    this_prices = prices.copy()
    current_rsi = calc_rsi(this_prices, period)

    length = len(current_rsi)

    if current_rsi[length - 1] < desired_rsi:
        return this_prices[length - 1]

    this_rsi = current_rsi[length - 1]

    while this_rsi > desired_rsi:
        this_prices[length - 1] = this_prices[length - 1] - price_offset
        rsi_minus_offset = calc_rsi(this_prices, period)
        this_rsi = rsi_minus_offset[length - 1]

    return this_prices[length - 1]
