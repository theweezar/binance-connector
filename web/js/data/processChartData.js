// src/data/processChartData.js
"use strict";

import { has } from "../utils/validators.js";

/**
 * Helper function to decide return values based on cell content
 * @param {Object} row - data row
 * @param {string} key - key to check in the row
 * @param {string} buyCst - value representing a buy signal
 * @param {string} sellCst - value representing a sell signal
 * @param {string} buyRet - return value if buy signal matches
 * @param {string} sellRet - return value if sell signal matches
 * @returns 
 */
function decide(row, key, buyCst, sellCst, buyRet, sellRet) {
  const val = row[key];
  if (val === buyCst) return buyRet;
  if (val === sellCst) return sellRet;
  return null;
}

/**
 * Create a candlestick object from a data row
 * @param {Object} row - data row
 * @returns {Object} candlestick object
 */
function createCandleObject(row) {
  return {
    open: Number(row.open),
    high: Number(row.high),
    low: Number(row.low),
    close: Number(row.close),
    raw: row
  };
}

/**
 * Create an entry marker based on buy/sell signals
 * @param {Object} row - data row
 * @param {string} baseKey - key to check in the row
 * @param {string} buyCst - value representing a buy signal
 * @param {string} sellCst - value representing a sell signal
 * @returns {Object|null} entry marker object or null if no marker
 */
function createEntryMarker(row, baseKey, buyCst, sellCst) {
  if (!has(row, baseKey)) return null;
  const color = decide(row, baseKey, buyCst, sellCst, "#4AFA9A", "#FF4976");
  if (!color) return null;
  const position = decide(row, baseKey, buyCst, sellCst, "belowBar", "aboveBar");
  const shape = decide(row, baseKey, buyCst, sellCst, "arrowUp", "arrowDown");
  const text = decide(row, baseKey, buyCst, sellCst, "B", "S");
  return { position, color, shape, text };
}

/**
 * Process chart data into structured format
 * @param {Array} data - array of data rows
 * @param {Object} config - configuration object
 * @returns {Object} structured chart data
 */
export function processChartData(data, config) {
  const seriesObject = {
    candle: { series: [] },
    marker: { series: [] },
    line: {},
    rawMapping: {},
    pane: {}
  };

  const lineSeriesCfg = config.LineSeries;
  if (Array.isArray(lineSeriesCfg)) {
    for (const [index, group] of lineSeriesCfg.entries()) {
      for (const [series, options] of Object.entries(group)) {
        seriesObject.line[series] = {
          series: [],
          index,
          options
        };
      }
    }
  }

  data.forEach(row => {
    const date = new Date(row.start);
    const time = date.getTime();

    seriesObject.candle.series.push({
      time, ...createCandleObject(row)
    });

    const marker = createEntryMarker(row, "entry_signal", "BUY", "SELL");
    if (marker) seriesObject.marker.series.push({
      time, ...marker
    });

    Object.keys(seriesObject.line).forEach(key => {
      if (has(row, key)) seriesObject.line[key].series.push({ time, value: Number(row[key]), });
    });

    seriesObject.rawMapping[time] = row;
  });

  return seriesObject;
}
