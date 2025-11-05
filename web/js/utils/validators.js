// src/utils/validators.js
"use strict";

export function has(obj, key) {
  return obj && obj[key] !== undefined && obj[key] !== null && obj[key] !== "" && obj[key] !== "-";
}

export function parseFixed(value, fixed) {
  const num = Number(value);
  return !isNaN(num) ? num.toFixed(fixed) : "";
}

export function getFractionDigits() {
  return 2;
}
