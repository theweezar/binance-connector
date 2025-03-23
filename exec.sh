#!/usr/bin/env bash

node ./js/cli.js price:frame -p "ignore" -s "XRP" -i "15m" -f 1
python ./py/processor.py ./ignore
# python ./py/draw.py ./ignore
python ./py/trainer.py
# python ./py/model.py

# node ./js/robot.js