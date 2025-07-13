#!/usr/bin/env bash

path="ignore/crypto"
symbol="XRP"
interval="1d"

# node ./js/cli.js price:frame -p $path/$symbol.csv -s $symbol -i $interval -f 30
# node ./js/cli.js price:period -p $path/$symbol.csv -s $symbol -i $interval -S "2022-07-11" -E "2025-07-12"
# python py/cli.py process --source=$path/$symbol.csv
# python py/cli.py train --source=$path/$symbol.csv --module=logistic_reg_model --export=$path/$symbol\_logistic_reg_model.pkl

# node js/cli.js price:frame -p $path/$symbol\_now.csv -s $symbol -i $interval -f 1
# python py/cli.py process --source=$path/$symbol\_now.csv
# python py/cli.py predict --source=$path/$symbol\_now.csv --model=$path/$symbol\_logistic_reg_model.pkl --timesteps=21

# python py/rsi.py reverse --source=$path/$symbol.csv --window=6 --offset=-0.01 --desired=15,20,25,35,45,55
# python py/rsi.py reverse --source=$path/$symbol.csv --window=6 --offset=0.01 --desired=86,87,88,89,90,91,92,93,94,95,96,97,98,99

# XLM
# python py/rsi.py reverse --source=$path/$symbol.csv --window=6 --offset=0.001 --desired=86,87,88,89,90,91,92,93,94,95,96,97,98,99

# python py/unify_cli.py unify --output=ignore/unify/unified_learning_2020_2025_data.csv --config=config/learning_unify.json
# python py/unify_cli.py unify --output=ignore/unify/unified_testing_2020_2025_data.csv --config=config/testing_unify.json --select="-23:"
# python py/unify_cli.py train --source=ignore/unify/unified_learning_2020_2025_data.csv
# python py/unify_cli.py predict --source=ignore/unify/unified_testing_2020_2025_data.csv --model=ignore/unified_model.pkl

python py/price.py fetch --symbol=BTCUSDT --interval=1d --path=ignore/btc.csv --chunk=3