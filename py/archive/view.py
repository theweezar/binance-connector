import matplotlib.pyplot as plt
import numpy as np
import util
import os
from chart import Chart


class View:
    def __init__(self, number_of_chart, initial_chart_nd_array: np.ndarray):
        figure, axs = plt.subplots(
            number_of_chart, 1, sharex="col", layout="constrained", figsize=(10, 12)
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
        export_dir = util.get_export_dir()
        image_dir = os.path.join(export_dir, "image")

        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        save_path = os.path.join(image_dir, "figure.png")
        self.figure.savefig(save_path)
        plt.close(self.figure)
