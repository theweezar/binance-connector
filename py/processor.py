import fire
from util import file
from processors import indicator


class Processor_CLI(object):
    """
    Command Line Interface for processing data using indicators.
    """

    def process(self, source, output):
        """
        Process the source data using a processor module.

        Args:
            source (str): The path to the source data.
            output (str): The path to the output data.
        """
        _source = file.get_source(source)

        print(f"Start processing data for {_source['filepath']}")

        dataframe = indicator.apply(_source["dataframe"])
        resolved_output = file.resolve(output)

        with open(resolved_output, "w") as f:
            f.write(dataframe.to_csv(index_label="index", lineterminator="\n"))

        print(f"Exported TA data to {resolved_output}")


if __name__ == "__main__":
    processor_cli = Processor_CLI()
    fire.Fire(processor_cli)
