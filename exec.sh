#!/usr/bin/env bash

path="ignore"
symbol="XRP"
interval="4h"

# node ./js/cli.js price:frame -p $path/$symbol.csv -s $symbol -i $interval -f 1
node ./js/cli.js price:period -p $path/$symbol.csv -s $symbol -i $interval -S "2025-01-01" -E "2025-03-20"
python py/cli.py process --source=$path/$symbol.csv
python py/cli.py train --source=$path/$symbol.csv --module=logistic_reg_model --export=$path/$symbol\_logistic_reg_model.pkl

# node js/cli.js price:frame -p $path/$symbol\_now.csv -s $symbol -i $interval -f 1
# python py/cli.py process --source=$path/$symbol\_now.csv
# python py/cli.py predict --source=$path/$symbol\_now.csv --model=$path/$symbol\_logistic_reg_model.pkl --timesteps=21