#!/usr/bin/env bash

node ./js/fetch.js -p "ignore" -s "BTC" -i "1h" -f 1 -D
python ./py/processor.py ./ignore
# python ./py/draw.py ./ignore
# python ./py/deep_learning_model.py ./ignore

node ./js/robot.js