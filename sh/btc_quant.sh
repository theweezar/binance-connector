#!/usr/bin/env bash

df=BTC-USDT_1h
interval=1h

python py/bingx.py run --symbol=BTC-USDT --interval=$interval --output=ignore/${df}.csv --chunk=1

python py/quantdeepseek.py run --input=ignore/${df}.csv --output=web/dist/file/${df}_deepseek.csv --strict=False
