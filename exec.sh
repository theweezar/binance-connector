#!/usr/bin/env bash

symbol="XRP"
interval="1h"

node ./js/cli.js price:period -p ignore/$symbol.csv -s $symbol -i "1h" -S "2025-01-01" -E "2025-03-20"
python py/cli.py process --source=ignore/$symbol.csv
python py/cli.py train --source=ignore/$symbol.csv --module=logistic_reg_model --export=ignore/$symbol\_logistic_reg_model.pkl

node js/cli.js price:frame -p ignore/$symbol\_now.csv -s $symbol -i "1h" -f 1
python py/cli.py process --source=ignore/$symbol\_now.csv
python py/cli.py predict --source=ignore/$symbol\_now.csv --model=ignore/$symbol\_logistic_reg_model.pkl --timesteps=20