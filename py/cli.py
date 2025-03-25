import fire
import re
import os
import pandas
import importlib
import pickle
from sklearn.linear_model import LogisticRegression
from pathlib import Path
from sklearn.metrics import accuracy_score

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


def preprocessing_data(
    dataframe: pandas.DataFrame,
) -> tuple[pandas.DataFrame, pandas.DataFrame, str]:
    """
    Preprocess the data for model training.

    Args:
        dataframe (pandas.DataFrame): The input dataframe.

    Returns:
        tuple: A tuple containing the features, target, and symbol.
    """
    data = dataframe.copy()
    symbol = data["symbol"][0]
    data.dropna(inplace=True)

    # Raw X values
    x_features = data[
        [
            "close",
            "ema_trend",
            "rsi_6",
            "rsi_9",
            "ema_34",
            "ema_89",
            "macd",
            "macd_signal",
            "adx_14",
        ]
    ]

    # Binary classification -> Up/Down -> raw y values
    y_target = (data["type"] == "U").astype(int)

    return x_features, y_target, symbol


def _export(path, model):
    """
    Export the trained model to a file.

    Args:
        path (str): The path to export the model.
        model: The trained model.
    """
    export_path = resolve(path)
    with open(export_path, "wb") as f:
        pickle.dump(model, f)
        print(f"Model exported to {export_path}")


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


"""
python py/cli.py train --source=ignore/export_20250324225400_binance_XRPUSDT_1h.csv --module=logistic_reg_model --export=ignore/model1.pkl
python py/cli.py use --source=ignore/export_20250324225400_binance_XRPUSDT_1h.csv --model=ignore/model1.pkl --timesteps=1
python py/cli.py process --source=ignore/export_20250324225400_binance_XRPUSDT_1h.csv
"""


class Model(object):
    def train(self, module, source, export=""):
        """
        Train a model using the provided module and source data.

        Args:
            module (str): The module to use for training.
            source (str): The path to the source data.
            export (str, optional): The path to export the trained model. Defaults to "".
        """
        _source = get_source(source)
        x, y, symbol = preprocessing_data(_source["dataframe"])

        print(f"Start analyzing price data for {symbol}")

        _module = importlib.import_module(module)
        _model = _module.train(x, y)

        if export != "":
            _export(export, _model)

    def predict(self, source, model, timesteps=60):
        """
        Predict using a trained model and source data.

        Args:
            source (str): The path to the source data.
            model (str): The path to the trained model.
            timesteps (int, optional): The number of timesteps for prediction. Defaults to 60.
        """
        _source = get_source(source)
        x, y, symbol = preprocessing_data(_source["dataframe"])
        model_path = resolve(model)
        _model = load(model_path)

        print(f"Start predicting price for {symbol}")

        _x = x[len(x) - (timesteps + 1) : len(x) - 1]
        _y = y[len(y) - (timesteps + 1) : len(y) - 1]
        y_pred = _model.predict(_x.values)

        print(f"Prediction:\n{y_pred}")
        print(f"Actual:\n{_y.values}")

        accuracy = accuracy_score(_y.values, y_pred)

        print(f"Model Accuracy: {accuracy:.2f}")


    def process(self, source):
        """
        Process the source data using a processor module.

        Args:
            source (str): The path to the source data.
        """
        _source = get_source(source)

        import processor

        print(f"Start processing data for {_source['filepath']}")

        dataframe = processor.process(_source["dataframe"])

        with open(_source["filepath"], "w") as f:
            f.write(dataframe.to_csv(index_label="index"))


if __name__ == "__main__":
    model = Model()
    fire.Fire(model)
