#!/usr/bin/env bash

node ./js/fetch.js -p "ignore" -s "LTC" -i "1h" -f 1
python ./py/processor.py ./ignore
# python ./py/draw.py ./ignore
# python ./py/trainer.py
python ./py/model.py

# node ./js/robot.js