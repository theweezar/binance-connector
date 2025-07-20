#!/usr/bin/env bash

symbol="$1"
interval="$2"
file_path="ignore/${symbol}_${interval}.csv"
ta_file_path="ignore/${symbol}_${interval}_ta.csv"
backtest_file_path="ignore/${symbol}_${interval}_backtest.csv"

python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path --merge=true --chunk=30
python py/rsi.py reverse --source=$file_path --window=6 --offset=$3 --desired=80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99 --price_type=high
python py/rsi.py reverse --source=$file_path --window=6 --offset=$4 --desired=25,24,23,22,21,20,19,18,17,16,15,14,13,12,11 --price_type=low
