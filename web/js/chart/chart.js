"use strict";

import { createChart, CandlestickSeries, createSeriesMarkers, LineSeries, ISeriesApi } from "lightweight-charts";
import { createTooltip } from "./tooltip.js";

export default class Chart {
  constructor(elementId, chartOptions = {}) {
    this.container = document.getElementById(elementId);
    if (!this.container) {
      throw new Error(`Element with id "${elementId}" not found`);
    }
    this.chart = createChart(this.container, chartOptions);
    this._tooltip = null;
    this._cache = {};
  }

  /**
   * Retrieve ISeries API to cache
   * @param {string} name - Series name
   * @param {ISeriesApi} series - ISeries API
   */
  saveSeries(name, series) {
    this._cache[name] = series;
  }

  /**
   * Retrieve ISeries API from cache
   * @param {string} seriesName - Series name
   * @returns {ISeriesApi} - ISeries API
   */
  retrieveSeries(seriesName) {
    return this._cache[seriesName];
  }

  // seriesArray is expected to be an array of candlestick points: [{ time, open, high, low, close }, ...]
  addSeries(seriesName, seriesArray, options) {
    const series = this.chart.addSeries(CandlestickSeries, options);
    series.setData(seriesArray);
    this.saveSeries(seriesName, series);
  }

  // markersArray is expected to be an array of marker objects supported by lightweight-charts
  addMarkersOn(seriesName, markersArray) {
    const series = this.retrieveSeries(seriesName);
    if (!series) {
      throw new Error("Series not initialized.");
    }
    if (Array.isArray(markersArray) && markersArray.length) {
      createSeriesMarkers(series, markersArray);
    }
  }

  // linesArray is expected to be an array of { id, data, options } where data is lightweight-charts style line points
  addLines(seriesName, linesArray, options) {
    const series = this.chart.addSeries(LineSeries, options);
    series.setData(linesArray);
    this.saveSeries(seriesName, series);
  }

  // callback: function(time, seriesDataPoint) => returns HTML string to be injected into tooltip
  addTooltipOn(seriesName, callback) {
    if (typeof callback !== "function") {
      throw new Error("Tooltip callback must be a function(time, data) returning HTML string");
    }

    if (!this._tooltip) {
      this._tooltip = createTooltip();
      this.container.appendChild(this._tooltip);
    }

    this.chart.subscribeCrosshairMove(param => {
      if (!param.time || !param.point) {
        this._tooltip.style.display = "none";
        return;
      }

      const series = this.retrieveSeries(seriesName);
      if (!series) {
        throw new Error("Series not initialized.");
      }

      const dataPoint = param.seriesData.get(series);
      try {
        const html = callback(param.time, dataPoint);
        if (typeof html === "string" && html.length > 0) {
          this._tooltip.innerHTML = html;
          this._tooltip.style.display = "block";
          this._tooltip.style.left = `${param.point.x + 15}px`;
          this._tooltip.style.top = "1rem";
        } else {
          this._tooltip.style.display = "none";
        }
      } catch (err) {
        this._tooltip.style.display = "none";
      }
    });
  }

  remove() {
    this.chart.remove();
  }

  getPaneByIndex(index) {
    const panes = this.chart.panes();
    return panes[index] || null;
  }
}
