"use strict";

import moment from "moment";
import Chart from "./chart.js";
import { processChartData } from "../data/processChartData.js";
import { getChartOptions, candlestickOptions, defaultLineOptions } from "../config/chartConfig.js";
import { createTooltipLine, createPaneTooltip } from "./tooltip.js";

export function createChartElement(data) {
  const globalCfg = window.config;
  const { candle, marker, line, rawMapping } = processChartData(data, globalCfg);
  const chartOptions = getChartOptions();
  const chart = new Chart("chartContainer", chartOptions);

  chart.addSeries("main", candle.series, candlestickOptions);

  // Lines
  for (const [key, model] of Object.entries(line)) {
    const options = { ...defaultLineOptions, ...model.options };
    chart.addLines(key, model.series, options);
    chart.retrieveSeries(key).moveToPane(model.index);

    // if (model.index == 0) continue; // Skip main pane
    // const paneEl = chart.getPaneByIndex(model.index).getHTMLElement();
    // const paneTooltip = createPaneTooltip();
    // paneTooltip.innerText = key;
    // paneEl?.querySelector("td:nth-child(2)").appendChild(paneTooltip);
    // console.log(chart.getPaneByIndex(model.index));
  }

  chart.addMarkersOn("main", marker.series);

  chart.addTooltipOn("main", (time, dataPoint) => {
    const price = dataPoint.value ?? dataPoint.close;
    const dateStr = moment(time).format("YYYY-MM-DD HH:mm:ss");
    const rawData = rawMapping[time] || {};
    const lines = [
      createTooltipLine("", price, "font-size:16px;margin-bottom:4px;color:black;font-weight:bold;"),
      createTooltipLine("Time", dateStr, "margin-bottom:2px;color:black;")
    ];

    for (const [key, column] of Object.entries(globalCfg.Tooltip)) {
      const value = typeof column.parseValue === "function" ? column.parseValue(rawData[column.value]) : rawData[column.value];
      lines.push(createTooltipLine(column.label, value, column.style));
    }

    return lines.join("");
  });

  window.chart = chart; 
}
