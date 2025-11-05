"use strict";

import { LineSeries, IChartApi } from "lightweight-charts";

/**
 * Line chart wrapper for Lightweight Charts.
 * @constructor
 * @param {IChartApi} chart - Chart instance.
 * @param {Array<Object>} data - Data for the line series.
 * @param {Object} options - Series options.
 * @param {string} controllerID - DOM element ID for controlling visibility.
 */
export default function Line(chart, data, options, controllerID) {
  this.chart = chart;
  this.data = data;
  this.options = options;
  this.series = null;
  this.controllerID = controllerID;
}

/**
 * Add the line series to the chart.
 */
Line.prototype.add = function () {
  this.series = this.chart.addSeries(LineSeries, this.options);
  this.series.setData(this.data);
};

/**
 * Remove the line series from the chart.
 */
Line.prototype.remove = function () {
  if (this.series) {
    this.chart.removeSeries(this.series);
    // this.series = null;
  }
};

/**
 * Initialize the controller for toggling the line series.
 */
Line.prototype.initController = function () {
  if (this.controllerID) {
    const controlEl = document.getElementById(this.controllerID);
    if (controlEl) {
      controlEl.addEventListener("change", (e) => {
        if (e.target.checked) {
          this.add();
        } else {
          this.remove();
        }
      });
    }
  }
};

/**
 * Render the line series.
 */
Line.prototype.render = function () {
  this.add();
  this.initController();
};
