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


def get_api() -> dict:
    export_dir_path = get_export_dir()
    api_path = os.path.join(export_dir_path, "api", "fetch.json")
    json_file = open(api_path)
    api_data = json.load(json_file)

    return api_data


def save_api(api_dict: dict):
    export_dir_path = get_export_dir()
    api_path = os.path.join(export_dir_path, "api", "fetch.json")

    with open(api_path, "w", encoding="utf-8") as json_file:
        json.dump(api_dict, json_file, ensure_ascii=False, indent=4)


def get_csv() -> dict[str, pandas.DataFrame]:
    export_dir_path = get_export_dir()
    api_data = get_api()
    file_name = api_data["fileName"]

    if re.search("(.csv$)", file_name) is None:
        raise Exception("CSV not found")

    csv_file_path = os.path.join(export_dir_path, file_name)

    return {
        "data_frame": pandas.read_csv(csv_file_path, sep=","),
        "file_name": file_name,
        "file_path": csv_file_path,
    }


def to_camelcase(string: str):
    p_string = string.lower().replace(" ", "_")
    return re.sub(r"(?!^)_([a-zA-Z0-9])", lambda m: m.group(1).upper(), p_string)
