import fire
from util import file
from processors import indicator
from termcolor import colored

class RSI_CLI(object):

    def reverse(self, source, window, offset, desired, price_type="close"):
        """
        Calculate the price if RSI reaches a desired value.

        Args:
            source (str): The path to the source data.
            window (int): The RSI window.
            offset (float): The price offset.
            desired (str): The desired RSI value list separate by comma (,).
            price_type (str): The type of price to use (default is "close").
        """
        _source = file.get_source(source)
        dataframe = _source["dataframe"]
        desired_list = list(desired)
        _offset = float(str(offset).strip())
        price_series = dataframe["close"]
        
        if price_type == "high":
            price_series = dataframe["high"]
        elif price_type == "low":
            price_series = dataframe["low"]

        for item in desired_list:
            desired_rsi = float(str(item).strip())

            if _offset > 0:
                price = indicator.calc_price_if_reverse_rsi_reach(
                    price_series, desired_rsi, window, _offset
                )
                print(colored(f"Price if RSI of \"{price_type}\" reaches {desired_rsi}: {price}", "red"))

            elif _offset < 0:
                price = indicator.calc_price_if_reverse_rsi_drop(
                    price_series, desired_rsi, window, _offset
                )
                print(colored(f"Price if RSI of \"{price_type}\" drops below {desired_rsi}: {price}", "green"))


if __name__ == "__main__":
    rsi_cli = RSI_CLI()
    fire.Fire(rsi_cli)
