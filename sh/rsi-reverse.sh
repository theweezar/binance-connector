#!/usr/bin/env bash

# ./sh/rsi-reverse.sh BTCUSDT 4h 50
symbol="$1"
interval="$2"
file_path="ignore/${symbol}_${interval}.csv"
ta_file_path="ignore/${symbol}_${interval}_ta.csv"
backtest_file_path="ignore/${symbol}_${interval}_backtest.csv"

python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path --merge=true --chunk=30
python py/rsi.py reverse --source=$file_path --window=9 --offset=$3 --desired=80,81,82,83,84,85,90,95 #--price_type=high
python py/rsi.py reverse --source=$file_path --window=9 --offset=-$3 --desired=25,20 #--price_type=low
