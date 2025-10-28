// src/config/chartConfig.js
'use strict';

import { CrosshairMode } from 'lightweight-charts';
import { parseFixed } from '../utils/validators.js';

export function getChartOptions({ fractionDigits }) {
  return {
    layout: {
      background: { color: '#1e1e1e' },
      textColor: '#D1D4DC',
    },
    grid: {
      vertLines: { color: '#2B2B43' },
      horzLines: { color: '#2B2B43' },
    },
    crosshair: { mode: CrosshairMode.Normal },
    localization: {
      priceFormatter: price => `${parseFixed(price, fractionDigits)}$`,
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
  };
}

export const candlestickOptions = {
  upColor: '#4AFA9A',
  downColor: '#FF4976',
  borderUpColor: '#4AFA9A',
  borderDownColor: '#FF4976',
  wickUpColor: '#4AFA9A',
  wickDownColor: '#FF4976',
};

export const defaultLineOptions = { lineWidth: 2 };
