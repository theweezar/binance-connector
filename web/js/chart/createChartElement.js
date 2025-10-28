// src/chart/createChartElement.js
'use strict';

import { createChart, CandlestickSeries, createSeriesMarkers } from 'lightweight-charts';
import moment from 'moment';
import Line from './line.js';
import { processChartData } from '../data/processChartData.js';
import { getChartOptions, candlestickOptions, defaultLineOptions } from '../config/chartConfig.js';
import { createTooltip, createTooltipLine } from './tooltip.js';
import { getFractionDigits } from '../utils/validators.js';

export function createChartElement(data, config) {
  const { candle, marker, line, rawMapping } = processChartData(data, config);

  const fractionDigits = getFractionDigits();
  const chartOptions = getChartOptions({ fractionDigits });

  const chartContainer = document.getElementById('chart-container');
  const chart = createChart(chartContainer, chartOptions);
  const candlestickSeries = chart.addSeries(CandlestickSeries, candlestickOptions);
  candlestickSeries.setData(candle.series);

  // Markers
  createSeriesMarkers(candlestickSeries, marker.series);

  // Tooltip
  const toolTip = createTooltip();
  chartContainer.appendChild(toolTip);

  chart.subscribeCrosshairMove(param => {
    if (!param.time || !param.point) {
      toolTip.style.display = 'none';
      return;
    }

    const dataPoint = param.seriesData.get(candlestickSeries);
    const price = dataPoint.value ?? dataPoint.close;
    const dateStr = moment(param.time).format('YYYY-MM-DD HH:mm:ss');
    const rawData = rawMapping[param.time] || {};

    const lines = [
      createTooltipLine('', price, 'font-size:16px;margin-bottom:4px;color:black;font-weight:bold;'),
      createTooltipLine('Time', dateStr, 'margin-bottom:2px;color:black;')
    ];

    Object.keys(config.Tooltip).forEach(key => {
      const t = config.Tooltip[key];
      const value = typeof t.parseValue === 'function' ? t.parseValue(rawData[t.value]) : rawData[t.value];
      lines.push(createTooltipLine(t.label, value, t.style));
    });

    toolTip.innerHTML = lines.join('');
    toolTip.style.display = 'block';
    toolTip.style.left = `${param.point.x + 15}px`;
    toolTip.style.top = '1rem';
  });

  // Lines
  Object.keys(line).forEach(key => {
    const options = config.LineSeries[key] || {};
    const lineObj = new Line(chart, line[key], { ...defaultLineOptions, ...options }, `line-${key}`);
    lineObj.render();
  });
}
