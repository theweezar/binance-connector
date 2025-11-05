// src/services/parser.js
"use strict";

import Papa from "papaparse";
import { createChartElement } from "../chart/createChartElement.js";

export function parseCSV(sourcePath, config) {
  Papa.parse(sourcePath, {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: results => {
      createChartElement(results.data, config);
    },
  });
}
