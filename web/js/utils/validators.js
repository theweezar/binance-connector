// src/utils/validators.js
"use strict";

/**
 * Check if an object has a valid value for a given key
 * @param {Object} obj - object to check
 * @param {string} key - key to check in the object
 * @returns {boolean} true if the object has a valid value for the key, false otherwise
 */
export function has(obj, key) {
  return obj && obj[key] !== undefined && obj[key] !== null && obj[key] !== "" && obj[key] !== "-";
}

/**
 * Parse a value to a fixed number of decimal places
 * @param {*} value - value to parse
 * @param {number} fixed - number of decimal places
 * @returns {string} parsed value as a string with fixed decimal places
 */
export function parseFixed(value, fixed) {
  const num = Number(value);
  return !isNaN(num) ? num.toFixed(fixed) : "";
}

/**
 * Get the number of fraction digits for formatting
 * @returns {number} number of fraction digits
 */
export function getFractionDigits() {
  return 2;
}
