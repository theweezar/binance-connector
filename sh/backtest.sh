#!/usr/bin/env bash

symbol="$1"
interval="$2"
file_path="ignore/${symbol}_${interval}.csv"
ta_file_path="ignore/${symbol}_${interval}_ta.csv"
backtest_file_path="ignore/${symbol}_${interval}_backtest.csv"

python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path --merge=true --chunk=60
python py/processor.py process --source=$file_path --output=$ta_file_path
python py/backtest.py compute --source=$ta_file_path --output=$backtest_file_path --tail=1000 --filter=select-max-min
python py/processor.py polyfit --source=$backtest_file_path --output=$backtest_file_path

cp $backtest_file_path web/dist/file/
echo "Copied backtest file to web/dist/file/"

offset="$3"
if [[ -n "$offset" ]]; then
    python py/rsi.py reverse --source=$file_path --window=5 --offset=$offset --desired=80,85,87,90 --price_type=high
    python py/rsi.py reverse --source=$file_path --window=5 --offset="-$offset" --desired=20,15 --price_type=low
fi