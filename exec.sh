#!/usr/bin/env bash

node ./js/fetch.js -p "ignore" -s "BTC" -i "15m" -f 1
# node ./js/fetch.js -p "ignore" -s "BTC" -i "1h" -b "3"
python ./py/processor.py ./ignore
# python ./py/draw.py ./ignore
# python ./py/trainer.py
# python ./py/model.py

# node ./js/robot.js