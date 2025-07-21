#!/usr/bin/env bash

symbol="$1"
interval="$2"
file_path="ignore/${symbol}_${interval}.csv"
ta_file_path="ignore/${symbol}_${interval}_ta.csv"
backtest_file_path="ignore/${symbol}_${interval}_backtest.csv"

python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path --merge=true --chunk=60
python py/processor.py process --source=$file_path --output=$ta_file_path
python py/backtest.py compute --source=$ta_file_path --output=$backtest_file_path --tail=1000 --filter=select-max-min

cp $backtest_file_path web/dist/file/
echo "Copied backtest file to web/dist/file/"