#!/usr/bin/env bash

node ./js/cli.js price:frame -p "ignore" -s "XRP" -i "15m" -f 3
python ./py/processor.py ./ignore
# python ./py/draw.py ./ignore
# python ./py/trainer.py
# python ./py/analyze_basic_logistic_reg.py ./ignore
# python ./py/model.py

# node ./js/robot.js