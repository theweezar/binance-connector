import re
import os
import pandas
import json
from sklearn.linear_model import LogisticRegression
from pathlib import Path
import pickle


def resolve(path: str) -> str:
    """
    Resolve the absolute path from a relative path.

    Args:
        path (str): The relative path.

    Returns:
        str: The absolute path.
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


def export_py_object(path: str, model: object):
    """
    Export the trained model to a file.

    Args:
        path (str): The path to export the model.
        model: The trained model.
    """
    export_path = resolve(path)
    existing = Path(export_path)
    if existing.is_file():
        print(f"Removed existing file: {export_path}")
        existing.unlink()

    with open(export_path, "wb") as f:
        pickle.dump(model, f)
        print(f"Model exported to {export_path}")


def write(path: str, content: str, mode="w"):
    """
    Write content to a file.
    """
    _path = resolve(path)

    with open(_path, mode) as f:
        f.write(content)


def load(path) -> LogisticRegression:
    """
    Load a trained model from a file.

    Args:
        path (str): The path to the model file.

    Returns:
        LogisticRegression: The loaded model.
    """
    with open(path, "rb") as f:
        _model = pickle.load(f)
    return _model

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

