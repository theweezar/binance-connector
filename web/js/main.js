// src/main.js
"use strict";

import { parseCSV } from "./services/parser.js";
import { getSource } from "./utils/url.js";
import { init as initTweakpane } from "./tweakpane/tweakpane.js";
import "../scss/bootstrap.scss";

/**
 * Set chart title
 * @param {string} title - Chart title
 */
function setChartTitle(title) {
  const chartTitle = document.getElementById("chartTitle");
  if (chartTitle) chartTitle.textContent = title;
}

/**
 * Initialize chart
 * @returns {void}
 */
function initChart() {
  const source = getSource();
  const csvUrl = `${location.origin}/dist/file/${source}`;

  if (!source) return;

  setChartTitle(source);
  parseCSV(csvUrl);

  document.body.addEventListener("parse:csv", () => {
    parseCSV(csvUrl);
  });
};

(function () {
  initTweakpane();
  initChart();
})();
