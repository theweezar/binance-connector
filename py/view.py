import matplotlib.pyplot as plt
import numpy as np
from chart import Chart


class View:
    def __init__(self, number_of_chart, initial_chart_nd_array: np.ndarray):
        figure, axs = plt.subplots(
            number_of_chart, 1, sharex="col", layout="constrained", figsize=(10, 10)
        )
        self.number_of_chart = number_of_chart
        self.charts = []
        self.figure = figure

        for i in range(number_of_chart):
            new_chart = Chart(axs[i])
            new_chart.set_initial_nd_array(initial_chart_nd_array)
            self.charts.append(new_chart)

    def get_chart(self, index) -> Chart:
        return self.charts[index]

    def show(self):
        plt.show()

    def export(self):
        self.figure.savefig("figure.png")
        plt.close(self.figure)
