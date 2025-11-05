// src/data/processChartData.js
"use strict";

import { has } from "../utils/validators.js";

function decise(row, key, buyCst, sellCst, buyRet, sellRet) {
  const val = row[key];
  if (val === buyCst) return buyRet;
  if (val === sellCst) return sellRet;
  return null;
}

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
    if (has(row, "position") || has(row, "sensitive_position")) {
      let isLong, color;

      if (has(row, "position")) {
        isLong = Number(row.position) === 1;
        color = isLong ? "#4AFA9A" : "#FF4976";
      }
      if (has(row, "sensitive_position")) {
        isLong = Number(row.sensitive_position) === 1;
        color = isLong ? "#FFFF00" : "#7C4DFF";
      }

      const price = isLong ? Number(row.low) : Number(row.high);

      seriesObject.marker.series.push({
        time,
        position: isLong ? "belowBar" : "aboveBar",
        color,
        shape: isLong ? "arrowUp" : "arrowDown",
        text: isLong ? `B: ${price}` : `S: ${price}`,
      });
    }

    if (has(row, "entry_signal")) {
      const color = decise(row, "entry_signal", "BUY", "SELL", "#4AFA9A", "#FF4976");
      const position = decise(row, "entry_signal", "BUY", "SELL", "belowBar", "aboveBar");
      const shape = decise(row, "entry_signal", "BUY", "SELL", "arrowUp", "arrowDown");
      const text = decise(row, "entry_signal", "BUY", "SELL", "B", "S");

      if (color !== null) {
        seriesObject.marker.series.push({
          time, position, color, shape, text
        });
      }
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
