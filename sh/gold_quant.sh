#!/usr/bin/env bash

df=XAUT-USDT_15m
interval=15m

# python py/bingx.py run --symbol=XAUT-USDT --interval=$interval --output=ignore/${df}.csv --chunk=1

# python py/quantchatgpt.py run --input=ignore/XAUT-USDT_15m.csv --output=web/dist/file/XAUT-USDT_15m_chatgpt.csv

python py/quantdeepseek.py run --input=ignore/${df}.csv --output=web/dist/file/${df}_deepseek.csv --strict=False

