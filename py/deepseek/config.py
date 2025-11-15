class Config:
    # === DATA & SYSTEM PARAMETERS ===

    # Number of historical periods to use for rule performance evaluation and weight calculation
    # Shorter windows adapt faster but may be noisy, longer windows are more stable but slower to adapt
    WINDOW_LOOKBACK = 90

    # Controls how aggressively the system favors top-performing rules in weight calculation
    # Higher values = more aggressive weighting (exponential scaling factor)
    SENSITIVITY_FACTOR = 10

    # === RSI INDICATOR PARAMETERS ===

    # Number of periods to calculate RSI (Relative Strength Index)
    # Shorter periods = more sensitive, longer periods = smoother signals
    RSI_PERIOD = 9

    # RSI level considered overbought (typically 70-80)
    # Values above this suggest potential price reversal downward
    RSI_OVERBOUGHT = 75

    # RSI level considered oversold (typically 20-30)
    # Values below this suggest potential price reversal upward
    RSI_OVERSOLD = 25

    # Period for moving average of RSI - smooths RSI to reduce noise and false signals
    # Helps identify RSI trend direction more clearly
    RSI_MA_PERIOD = 5

    # RSI moving average method:
    # 'sma' -
    # 'ema' -
    RSI_MA_METHOD = "ema"

    RSI_CROSS_OVERBOUGHT = 70

    RSI_CROSS_OVERSOLD = 30

    # MACD Indicator Parameters
    # Default: (12, 26, 9)
    # For day trading: (5, 13, 9) or (8, 21, 5) for more sensitivity
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGN = 9

    # === MOVING AVERAGE PARAMETERS ===

    # Short-term Simple Moving Average period for crossover signals
    # More responsive to recent price changes
    MA_SHORT = 9

    # Long-term Simple Moving Average period for crossover signals
    # Represents longer-term trend direction
    MA_LONG = 21

    # === EXPONENTIAL MOVING AVERAGE PARAMETERS ===

    # Short-term EMA period - gives more weight to recent prices than SMA
    # Faster response to price changes than regular MA
    EMA_SHORT = 9

    # Long-term EMA period - smooths long-term trend
    # Popular combination: 9 & 21 EMAs
    EMA_LONG = 21

    # === BOLLINGER BANDS PARAMETERS ===

    # Period for calculating Bollinger Bands middle line (SMA)
    # Standard setting is 20 periods
    BB_PERIOD = 20

    # Number of standard deviations for upper/lower band width
    # Higher values = wider bands, more extreme signals
    BB_STD = 2

    # === TRADING & RISK PARAMETERS ===

    # Starting capital for backtesting and portfolio simulation
    INITIAL_CAPITAL = 100000

    # Lookback period for identifying support/resistance levels
    # Longer periods find more significant levels but may be less relevant
    SUPPORT_RESISTANCE_LOOKBACK = 20

    # Period for volume moving average calculation
    # Used to identify above/below average volume conditions
    VOLUME_MA_PERIOD = 20

    # Minimum volume multiplier to consider volume "strong"
    # 1.1 = 10% above average volume required for volume confirmation
    MIN_VOLUME_STRENGTH = 1.1

    # === SIGNAL THRESHOLD PARAMETERS ===

    # Base threshold for composite signal to trigger trades (0.0 to 1.0)
    # Higher values = fewer but higher conviction trades
    BASE_THRESHOLD = 0.25

    # Minimum allowed threshold regardless of adaptive calculations
    # Prevents system from becoming too sensitive
    MIN_THRESHOLD = 0.1

    # Maximum allowed threshold regardless of adaptive calculations
    # Prevents system from becoming too conservative
    MAX_THRESHOLD = 0.4

    # Threshold adjustment method:
    # 'fixed' - uses BASE_THRESHOLD consistently
    # 'adaptive' - adjusts based on number of active rules
    # 'volatility' - adjusts based on market volatility (higher vol = higher threshold)
    THRESHOLD_METHOD = "fixed"

    ADAPTIVE_THRESHOLD = 0.3

    # === PRICE ACTION PARAMETERS ===

    # Lookback period for identifying supply/demand zones
    # How far back to search for significant rejection areas
    SUPPLY_DEMAND_LOOKBACK = 20

    # Minimum wick-to-body ratio to qualify as supply/demand zone
    # Higher values = more significant rejection required
    SUPPLY_DEMAND_MIN_STRENGTH = 2.0

    # Number of bars on each side to identify swing highs/lows
    # Used for market structure analysis
    SWING_POINT_LENGTH = 5

    # Lookback period for volume profile analysis
    # How much history to consider for volume concentration areas
    VOLUME_PROFILE_LOOKBACK = 50

    # Volume multiplier to identify significant volume spikes
    # 1.5 = 50% above average volume considered a spike
    VOLUME_SPIKE_THRESHOLD = 1.5

    # Lookback period for order flow imbalance calculation
    # How many recent bars to analyze for buy/sell pressure
    ORDER_FLOW_LOOKBACK = 10

    # Minimum wick-to-body ratio for price rejection patterns
    # Identifies significant pin bars and rejection candles
    REJECTION_MIN_WICK_RATIO = 2.0
