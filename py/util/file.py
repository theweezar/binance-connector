import re
import os
import pandas
import json
from pathlib import Path


def resolve(path: str) -> Path:
    """
    Resolve the absolute path from a relative path.

    Args:
        path (str): The relative path.

    Returns:
        Path: The absolute path.
    """
    return Path(os.path.join(os.getcwd(), path)).resolve()


def get_source(source: str) -> dict[str, pandas.DataFrame, str]:
    """
    Get the source data from a CSV file.

    Args:
        source (str): The path to the CSV file.

    Returns:
        dict: A dictionary containing the dataframe, filename, and filepath.
    """
    if re.search("(.csv$)", source) is None:
        raise Exception("CSV not found")

    source_path = resolve(source)
    path_split = os.path.split(source_path)

    return {
        "dataframe": pandas.read_csv(source_path, sep=","),
        "filename": path_split[1],
        "filepath": source_path,
    }


def write(path: str, content: str, mode="w"):
    """
    Write content to a file.
    """
    _path = resolve(path)

    with open(_path, mode) as f:
        f.write(content)


def require(path: str) -> dict:
    """
    Load JSON file.

    Args:
        path (str): The path to the JSON file.

    Returns:
        *: The JSON data.
    """
    _path = resolve(path)
    if not os.path.exists(_path):
        e = "File not found: {_path}".format(_path=_path)
        raise FileNotFoundError(e)
    with open(_path, "r") as json_file:
        return json.load(json_file)
