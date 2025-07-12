#!/usr/bin/env bash

symbol="XRPUSDT"
interval="1h"
file_path="ignore/${symbol}_${interval}.csv"

# python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path --chunk=3
python py/price.py fetch --symbol=$symbol --interval=$interval --path=$file_path --from_=2023-01-01 --to=2025-07-12
python py/cli.py rsi_reverse --source=$file_path --window=6 --offset=0.01 --desired=55,60,65,70,75,80,85,90,95
