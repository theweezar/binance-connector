// src/services/parser.js
"use strict";

import Papa from "papaparse";
import { createChartElement } from "../chart/createChartElement.js";

/**
 * Parse CSV from source path and create chart element
 * @param {string} sourcePath - Source path of the CSV file
 */
export function parseCSV(sourcePath) {
  console.log("Loading CSV from:", sourcePath);
  Papa.parse(sourcePath, {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: (results) => {
      createChartElement(results.data);
    },
  });
}
