#!/usr/bin/env bash

symbol="BTCUSDT"
interval="1h"
file_path="ignore/${symbol}_${interval}.csv"

# python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path  --merge=true
python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path --chunk=30
# python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path --from_=2022-01-01 --to=2025-07-13
# python py/rsi.py reverse --source=$file_path --window=6 --offset=0.01 --desired=75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99
