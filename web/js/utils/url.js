"use strict";

export function getSource() {
  const url = new URL(location.href);
  const source = url.searchParams.get("source");
  return source || "";
}