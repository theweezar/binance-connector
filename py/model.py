import fire
import importlib
from util import file, object as obj
from sklearn.metrics import accuracy_score
from processors import preprocessor


class Model(object):
    def train(self, module, source, export=""):
        """
        Train a model using the provided module and source data.

        Args:
            module (str): The module to use for training.
            source (str): The path to the source data.
            export (str, optional): The path to export the trained model. Defaults to "".
        """
        df = file.get_source(source)
        x, y, symbol = preprocessor.process_data(df, dropna=True)

        print(f"Start analyzing price data for {symbol}")

        _module = importlib.import_module(module)
        _model = _module.train(x.values, y.values)

        if export != "":
            obj.export(export, _model)

    def predict(self, source, model, timesteps=60):
        """
        Predict using a trained model and source data.

        Args:
            source (str): The path to the source data.
            model (str): The path to the trained model.
            timesteps (int, optional): The number of timesteps for prediction. Defaults to 60.
        """
        df = file.get_source(source)
        x, y, symbol = preprocessor.process_data(df, dropna=False)
        model_path = file.resolve(model)
        _model = obj.load(model_path)

        print(f"Start predicting price for {symbol}")

        _x = x[len(x) - (timesteps + 1) : len(x) - 1]
        _y = y[len(y) - (timesteps + 1) : len(y) - 1]
        y_pred = _model.predict(_x.values)

        print(f"Prediction:\n{y_pred}")
        print(f"Actual:\n{_y.values}")

        accuracy = accuracy_score(_y.values, y_pred)

        print(f"Model Accuracy: {accuracy:.2f}")


if __name__ == "__main__":
    model = Model()
    fire.Fire(model)
