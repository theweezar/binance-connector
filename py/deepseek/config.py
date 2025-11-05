# Trading system configuration
class Config:
    LOOKBACK_WINDOW = 90
    SENSITIVITY_FACTOR = 10

    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    MA_SHORT = 50
    MA_LONG = 200
    BB_PERIOD = 20
    BB_STD = 2

    INITIAL_CAPITAL = 100000


# In config.py - CREATE A 15M CONFIG:
class Config15M:
    # Shorter periods for 15m data
    LOOKBACK_WINDOW = 90
    SENSITIVITY_FACTOR = 15

    RSI_PERIOD = 9
    RSI_OVERBOUGHT = 65
    RSI_OVERSOLD = 35
    MA_SHORT = 5
    MA_LONG = 20
    BB_PERIOD = 20
    BB_STD = 2

    INITIAL_CAPITAL = 100000
