import fire
import importlib
from util import file
from sklearn.metrics import accuracy_score
from processor import indicator, preprocessor


class Model(object):
    def train(self, module, source, export=""):
        """
        Train a model using the provided module and source data.

        Args:
            module (str): The module to use for training.
            source (str): The path to the source data.
            export (str, optional): The path to export the trained model. Defaults to "".
        """
        _source = file.get_source(source)
        x, y, symbol = preprocessor.process_data(_source["dataframe"], dropna=True)

        print(f"Start analyzing price data for {symbol}")

        _module = importlib.import_module(module)
        _model = _module.train(x.values, y.values)

        if export != "":
            file.export_py_object(export, _model)

    def predict(self, source, model, timesteps=60):
        """
        Predict using a trained model and source data.

        Args:
            source (str): The path to the source data.
            model (str): The path to the trained model.
            timesteps (int, optional): The number of timesteps for prediction. Defaults to 60.
        """
        _source = file.get_source(source)
        x, y, symbol = preprocessor.process_data(_source["dataframe"], dropna=False)
        model_path = file.resolve(model)
        _model = file.load(model_path)

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
        _source = file.get_source(source)

        print(f"Start processing data for {_source['filepath']}")

        dataframe = indicator.apply(_source["dataframe"])

        with open(_source["filepath"], "w") as f:
            f.write(dataframe.to_csv(index_label="index", lineterminator="\n"))

    def rsi_reverse(self, source, window, offset, desired):
        """
        Calculate the price if RSI reaches a desired value.

        Args:
            source (str): The path to the source data.
            window (int): The RSI window.
            offset (float): The price offset.
            desired (str): The desired RSI value list separate by comma (,).
        """
        _source = file.get_source(source)
        dataframe = _source["dataframe"]
        close = dataframe["close"]
        desired_list = list(desired)
        _offset = float(str(offset).strip())

        for item in desired_list:
            desired_rsi = float(str(item).strip())

            if _offset > 0:
                price = indicator.calc_price_if_reverse_rsi_reach(
                    close, desired_rsi, window, _offset
                )
                print(f"Price if RSI reaches {desired_rsi}: {price}")

            elif _offset < 0:
                price = indicator.calc_price_if_reverse_rsi_drop(
                    close, desired_rsi, window, _offset
                )
                print(f"Price if RSI drops below {desired_rsi}: {price}")


if __name__ == "__main__":
    model = Model()
    fire.Fire(model)
