#!/usr/bin/env bash

node ./js/cli.js price:frame -s "XRP" -i "1h" -f 1
# node ./js/cli.js price:period -s "XRP" -i "1h" -S "2025-01-01" -E "2025-03-24"
# node ./js/cli.js price:period -s "XRP" -i "1h" -S "2025-03-24" -E "2025-03-25"
python ./py/processor.py ./ignore
# python ./py/draw.py ./ignore
# python ./py/trainer.py
# python ./py/analyze_basic_logistic_reg.py ./ignore
# python ./py/model.py

# node ./js/robot.js