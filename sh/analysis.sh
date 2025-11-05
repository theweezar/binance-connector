#!/usr/bin/env bash

# ./sh/analysis.sh XRPUSDT
# ./sh/analysis.sh TONUSDT
# ./sh/analysis.sh BTCUSDT
symbol="$1"

if [ -z "$symbol" ]; then
    echo "Usage: $0 <symbol>"
    exit 1
fi

# Fetch price data in chart 15m, 1h, and 4h intervals
# interval_15m="15m"
# file_path="ignore/${symbol}_${interval_15m}.csv"
# ta_file_path_15m="ignore/${symbol}_${interval_15m}_ta.csv"
# python py/price.py fetch --symbol=$symbol --interval=$interval_15m --path=$file_path --merge=true --chunk=30
# python py/processor.py process --source=$file_path --output=$ta_file_path_15m

interval_1h="1h"
file_path="ignore/${symbol}_${interval_1h}.csv"
ta_file_path_1h="ignore/${symbol}_${interval_1h}_ta.csv"
python py/price.py fetch --symbol=$symbol --interval=$interval_1h --path=$file_path --merge=true --chunk=30
python py/processor.py process --source=$file_path --output=$ta_file_path_1h

interval_2h="2h"
file_path="ignore/${symbol}_${interval_2h}.csv"
ta_file_path_2h="ignore/${symbol}_${interval_2h}_ta.csv"
python py/price.py fetch --symbol=$symbol --interval=$interval_2h --path=$file_path --merge=true --chunk=30
python py/processor.py process --source=$file_path --output=$ta_file_path_2h

interval_4h="4h"
file_path="ignore/${symbol}_${interval_4h}.csv"
ta_file_path_4h="ignore/${symbol}_${interval_4h}_ta.csv"
python py/price.py fetch --symbol=$symbol --interval=$interval_4h --path=$file_path --merge=true --chunk=30
python py/processor.py process --source=$file_path --output=$ta_file_path_4h

datetime=$(date +%Y-%m-%d_%H)
analyze_file="ignore/analyze_${symbol}_${datetime}.txt"

# Run analysis on the processed files
printf "\n"
printf "Upon observation, the chart is showing factors:" | tee $analyze_file
# python py/analysis.py analyze --source=$ta_file_path_15m --interval=$interval_15m | tee -a $analyze_file
python py/analysis.py analyze --source=$ta_file_path_1h --interval=$interval_1h | tee -a $analyze_file
python py/analysis.py analyze --source=$ta_file_path_2h --interval=$interval_2h | tee -a $analyze_file
python py/analysis.py analyze --source=$ta_file_path_4h --interval=$interval_4h | tee -a $analyze_file

footer="\
\nBased on factors, analyze, then print tables including:
- Timeframe-by-Timeframe tables (each table for each timeframe) with columns: Signal or Factor, Reading or Detail, Interpretation, Implication
- SUMMARY - Market Structure Overview table with columns: Timeframe, Trend, Momentum, Signal
- FORECAST - What's Likely to Happen table with columns: Scenario, Probability, Why
- STRATEGY Suggestion table with columns: Type, Suggested Action
Note: Add colors, or icons to highlight important factors, signals, or trends in the tables."

printf "$footer" | tee -a $analyze_file