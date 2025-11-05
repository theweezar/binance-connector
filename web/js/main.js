// src/main.js
"use strict";

import { parseCSV } from "./services/parser.js";
import "../scss/bootstrap.scss";

(function init() {
  const url = new URL(location.href);
  const path = "dist/file";
  const origin = location.origin;
  const source = url.searchParams.get("source");
  const chartTitle = document.getElementById("chartTitle");
  const csvPath = `${origin}/${path}/${source}`;

  if (source) {
    window.source = source;
    chartTitle.textContent = `${source}`;
    console.log("Loading CSV from:", csvPath);
    parseCSV(csvPath, window.config);
  }
})();
