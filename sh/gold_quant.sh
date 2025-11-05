#!/usr/bin/env bash

python py/bingx.py run --symbol=XAUT-USDT --interval=15m --output=ignore/XAUT-USDT_15m.csv --chunk=3

# python py/quantchatgpt.py run --input=ignore/XAUT-USDT_15m.csv --output=web/dist/file/XAUT-USDT_15m_chatgpt.csv

python py/quantdeepseek.py run --input=ignore/XAUT-USDT_15m.csv --output=web/dist/file/XAUT-USDT_15m_deepseek.csv --strict=True

