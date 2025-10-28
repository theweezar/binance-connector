#!/usr/bin/env bash

python py/bingx.py run --symbol=XAUT-USDT --interval=1h --output=ignore/XAUT-USDT_1h.csv --chunk=1
python py/quantchatgpt.py run --input=ignore/XAUT-USDT_1h.csv --output=web/dist/file/XAUT-USDT_1h_quant.csv

