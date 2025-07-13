import fire
from util import file
from processors import indicator


class RSI_CLI(object):

    def reverse(self, source, window, offset, desired):
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
    rsi_cli = RSI_CLI()
    fire.Fire(rsi_cli)
