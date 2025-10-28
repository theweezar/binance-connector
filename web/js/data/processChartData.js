// src/data/processChartData.js
'use strict';

import { has } from '../utils/validators.js';

export function processChartData(data, config) {
  const seriesObject = {
    candle: { series: [] },
    marker: { series: [] },
    line: {},
    rawMapping: {}
  };

  Object.keys(config.LineSeries).forEach(key => {
    seriesObject.line[key] = [];
  });

  data.forEach(row => {
    const date = new Date(row.start);
    const time = date.getTime();

    // Candlestick series
    seriesObject.candle.series.push({
      time,
      open: Number(row.open),
      high: Number(row.high),
      low: Number(row.low),
      close: Number(row.close),
      raw: row
    });

    // Marker creation
    if (has(row, 'position') || has(row, 'sensitive_position')) {
      let isLong, color;

      if (has(row, 'position')) {
        isLong = Number(row.position) === 1;
        color = isLong ? '#4AFA9A' : '#FF4976';
      }
      if (has(row, 'sensitive_position')) {
        isLong = Number(row.sensitive_position) === 1;
        color = isLong ? '#FFFF00' : '#7C4DFF';
      }

      const price = isLong ? Number(row.low) : Number(row.high);

      seriesObject.marker.series.push({
        time,
        position: isLong ? 'belowBar' : 'aboveBar',
        color,
        shape: isLong ? 'arrowUp' : 'arrowDown',
        text: isLong ? `B: ${price}` : `S: ${price}`,
      });
    }

    if (has(row, 'entry_signal') && Number(row.entry_signal) !== 0) {
      const isLong = Number(row.entry_signal) === 1;
      const color = isLong ? '#4AFA9A' : '#FF4976';
      const price = isLong ? Number(row.low) : Number(row.high);

      seriesObject.marker.series.push({
        time,
        position: isLong ? 'belowBar' : 'aboveBar',
        color,
        shape: isLong ? 'arrowUp' : 'arrowDown',
        // text: isLong ? `B: ${price}` : `S: ${price}`,
        text: isLong ? `B` : `S`,
      });
    }

    // Moving average lines
    Object.keys(seriesObject.line).forEach(key => {
      if (has(row, key)) {
        seriesObject.line[key].push({
          time,
          value: Number(row[key]),
        });
      }
    });

    seriesObject.rawMapping[time] = row;
  });

  return seriesObject;
}
