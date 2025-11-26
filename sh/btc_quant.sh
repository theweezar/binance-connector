#!/usr/bin/env bash

interval=15m
df=BTC-USDT_$interval

python py/bingx.py run --symbol=BTC-USDT --interval=$interval --output=ignore/${df}.csv --chunk=1
python py/quantdeepseek.py run --input=ignore/${df}.csv --output=web/dist/file/${df}_deepseek.csv
