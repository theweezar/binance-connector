"use strict";

(function () {
  /**
   * Format a number to a fixed decimal string.
   * @param {number} value - The number to format.
   * @param {number} fixed - The number of decimal places.
   * @returns {string} - Formatted number as a string.
   */
  function parseFixed(value, fixed) {
    var num = Number(value);
    return !isNaN(num) ? num.toFixed(fixed) : "";
  }

  window.config = {
    LineSeries: [
      {
        ema_short: {
          color: "#39e75f"
        },
        ema_long: {
          color: "#f7b731"
        }
      },
      {
        rsi: {
          color: "#c4d5e3"
        }
      },
      {
        adx: {
          color: "#f4d5e3"
        }
      }
    ],
    Tooltip: [
      {
        label: "High",
        value: "high",
        style: "margin-bottom: 2px; color: black;"
      },
      {
        label: "Low",
        value: "low",
        style: "margin-bottom: 2px; color: black;"
      },
      {
        label: "RSI",
        value: "rsi",
        parseValue: (value) => parseFixed(value, 2),
        style: "margin-bottom: 2px; color: black;"
      },
      {
        label: "ADX",
        value: "adx",
        parseValue: (value) => parseFixed(value, 2),
        style: "margin-bottom: 2px; color: black;"
      }
    ]
  };
})();
