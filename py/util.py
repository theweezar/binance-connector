import pandas
import os
import re
import sys
import json

def get_export_dir():
    cwd = os.getcwd()
    export_dir_path = ""

    if len(sys.argv) == 2:
        export_dir_path = os.path.join(cwd, sys.argv[-1])
    else:
        export_dir_path = os.path.join(cwd, "binance-connector", "ignore")

    return export_dir_path

def get_csv() -> dict[str, pandas.DataFrame]:
    export_dir_path = get_export_dir()
    json_file = open(os.path.join(export_dir_path, "api", "fetch.json"))
    fetch_data = json.load(json_file)
    file_name = fetch_data["fileName"]

    if re.search("(.csv$)", file_name) is None:
        raise Exception("CSV not found")

    csv_file_path = os.path.join(export_dir_path, file_name)

    return {
        "data_frame": pandas.read_csv(csv_file_path, sep=","),
        "file_name": file_name,
        "file_path": csv_file_path
    }