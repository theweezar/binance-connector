#!/usr/bin/env bash

source="$1"
config="$2"
allowed_rules="$3"

python py/quantdeepseek.py run_specific_config --input=ignore/$source --output=web/dist/file/$source --config="$config" --allowed_rules="$allowed_rules"