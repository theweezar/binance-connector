"use strict";

export function getSource() {
  const url = new URL(location.href);
  const source = url.searchParams.get("source");
  return source || "";
}

export function getSourceObject() {
  const source = getSource();
  const name = source.split(".")[0];
  const parts = name.split("_");
  return {
    symbol: parts[0],
    interval: parts[1]
  };
}