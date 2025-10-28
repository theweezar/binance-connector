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
        df = file.get_source(source)

        if isinstance(desired, int):
            desired_list = [desired]
        else:
            desired_list = list(desired)

        _offset = float(str(offset).strip())
        price_series = df["close"]

        if price_type == "high":
            price_series = df["high"]
        elif price_type == "low":
            price_series = df["low"]

        for item in desired_list:
            desired_rsi = float(str(item).strip())

            if _offset > 0:
                price = indicator.calc_price_if_reverse_rsi_reach(
                    price_series, desired_rsi, window, _offset
                )
                print(
                    colored(
                        f'Price if RSI ({window}) of "{price_type}" reaches {desired_rsi}: {str(price)}',
                        "red",
                    )
                )

            elif _offset < 0:
                price = indicator.calc_price_if_reverse_rsi_drop(
                    price_series, desired_rsi, window, _offset
                )
                print(
                    colored(
                        f'Price if RSI ({window}) of "{price_type}" drops below {desired_rsi}: {str(price)}',
                        "green",
                    )
                )


if __name__ == "__main__":
    rsi_cli = RSI_CLI()
    fire.Fire(rsi_cli)
