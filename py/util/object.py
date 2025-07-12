import os
import pickle
import file
from pathlib import Path
from sklearn.linear_model import LogisticRegression


def load(path) -> LogisticRegression:
    """
    Load a trained model from a file.

    Args:
        path (str): The path to the model file.

    Returns:
        LogisticRegression: The loaded model.
    """
    _path = file.resolve(path)
    if not os.path.exists(_path):
        e = "Can not load file. File not found: {_path}".format(_path=_path)
        raise FileNotFoundError(e)
    with open(path, "rb") as f:
        _model = pickle.load(f)
    return _model


def export(path: str, model: object):
    """
    Export the trained model to a file.

    Args:
        path (str): The path to export the model.
        model: The trained model.
    """
    export_path = file.resolve(path)
    existing = Path(export_path)
    if existing.is_file():
        print(f"Removed existing file: {export_path}")
        existing.unlink()

    with open(export_path, "wb") as f:
        pickle.dump(model, f)
        print(f"Model exported to {export_path}")
