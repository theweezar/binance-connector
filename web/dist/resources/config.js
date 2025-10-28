/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (function() { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./web/js/config.js":
/*!**************************!*\
  !*** ./web/js/config.js ***!
  \**************************/
/***/ (function() {

eval("{\n\n(function () {\n  /**\r\n   * Format a number to a fixed decimal string.\r\n   * @param {number} value - The number to format.\r\n   * @param {number} fixed - The number of decimal places.\r\n   * @returns {string} - Formatted number as a string.\r\n   */\n  function parseFixed(value, fixed) {\n    var num = Number(value);\n    return !isNaN(num) ? num.toFixed(fixed) : '';\n  }\n  window.config = {\n    LineSeries: {\n      // ma_20: {\n      //     color: '#39e75f'\n      // },\n      // ma_50: {\n      //     color: '#f7b731'\n      // },\n      // ma_9: {\n      //     color: '#39e75f'\n      // },\n      // ma_21: {\n      //     color: '#f7b731'\n      // },\n      ema_fast: {\n        color: '#39e75f'\n      },\n      ema_slow: {\n        color: '#f7b731'\n      }\n      // ema_50: {\n      //     color: '#f7b731'\n      // }\n      // support: {\n      //     color: '#00FF00',\n      // },\n      // resistance: {\n      //     color: '#FF0000',\n      // }\n    },\n    Tooltip: [{\n      label: 'High',\n      value: 'high',\n      style: 'margin-bottom: 2px; color: black;'\n    }, {\n      label: 'Low',\n      value: 'low',\n      style: 'margin-bottom: 2px; color: black;'\n    }, {\n      label: 'RSI (9)',\n      value: 'rsi_9',\n      parseValue: function parseValue(value) {\n        return parseFixed(value, 2);\n      },\n      style: 'margin-bottom: 2px; color: black;'\n    }\n    // {\n    //     label: 'RSI high (9)',\n    //     value: 'rsi_9_high',\n    //     parseValue: (value) => parseFixed(value, 2),\n    //     style: 'margin-bottom: 2px; color: red;'\n    // },\n    // {\n    //     label: 'RSI low (9)',\n    //     value: 'rsi_9_low',\n    //     parseValue: (value) => parseFixed(value, 2),\n    //     style: 'margin-bottom: 2px; color: green;'\n    // }\n    ]\n  };\n})();\n\n//# sourceURL=webpack://binance-connector/./web/js/config.js?\n}");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./web/js/config.js"]();
/******/ 	
/******/ })()
;