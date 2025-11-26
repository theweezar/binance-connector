"use strict";

import { Pane } from "tweakpane";
import { getSource } from "../utils/url";
import cfgPaneJson from "./configpane.json";
import rulePaneJson from "./rulepane.json";

function adjustHeight() {
  const tabWrapperEl = document.getElementById("myTab");
  const settingTabEl = document.getElementById("settings");
  const validHeight = window.innerHeight - tabWrapperEl.clientHeight - 8;
  settingTabEl.style.height = `${validHeight}px`;
  settingTabEl.style.overflowY = "scroll";
}

/**
 * Extract pane state into a simple object
 * @param {Pane} pane - Pane
 * @returns {Object} - State object
 */
function getState(pane) {
  const state = pane.exportState();
  const children = Array.isArray(state.children) ? state.children : [];
  const entries = children.flatMap(
    folder => Array.isArray(folder.children) ? folder.children.map(bindingEl =>
      [bindingEl.binding.key, bindingEl.binding.value]
    ) : []
  );
  return Object.fromEntries(entries);
};

/**
 * Import pane state from localStorage if exists
 * @param {Pane} pane - Pane
 * @param {string} stateName - State name in localStorage
 */
function importStateIfExists(pane, stateName) {
  try {
    const state = localStorage.getItem(stateName);
    if (state) pane.importState(JSON.parse(state));
  } catch (error) {
    console.error("Error importing state:", error);
  }
}

/**
 * Export pane state to localStorage
 * @param {Pane} pane - Pane
 * @param {string} stateName - State name in localStorage
 */
function exportStateToLocalStorage(pane, stateName) {
  try {
    const state = pane.exportState();
    localStorage.setItem(stateName, JSON.stringify(state));
  } catch (error) {
    console.error("Error exporting state:", error);
  }
}

/**
 * Initialize configuration pane
 * @returns {Pane} - Config Pane
 */
function initConfigPane() {
  const config = {};
  cfgPaneJson.forEach((section) => {
    (section.params || []).forEach((p) => {
      config[p.label] = p.value;
    });
  });

  const configPane = new Pane({
    container: document.getElementById("tweakpane-container"),
    title: "Settings"
  });

  // Create folders and bindings for each param pointing at config
  cfgPaneJson.forEach((section) => {
    const folder = configPane.addFolder({ title: section.folder });
    (section.params || []).forEach((p) => {
      folder.addBinding(config, p.label, { label: p.label });
    });
  });

  configPane.on("change", () => {
    exportStateToLocalStorage(configPane, "tp_configPaneState");
  });
  importStateIfExists(configPane, "tp_configPaneState");

  return configPane;
}

/**
 * Initialize rule pane
 * @returns {Pane} - Rule Pane
 */
function initRulePane() {
  const config = {};
  rulePaneJson.forEach((section) => {
    (section.params || []).forEach((p) => {
      config[p.label] = p.value;
    });
  });

  const rulePane = new Pane({
    container: document.getElementById("rulepane-container"),
    title: "Trading Rules"
  });

  rulePaneJson.forEach((section) => {
    const folder = rulePane.addFolder({ title: section.folder });
    (section.params || []).forEach((p) => {
      folder.addBinding(config, p.label, { label: p.title || p.label });
    });
  });

  rulePane.on("change", () => {
    exportStateToLocalStorage(rulePane, "tp_rulePaneState");
  });
  importStateIfExists(rulePane, "tp_rulePaneState");

  return rulePane;
}

export function init() {
  adjustHeight();

  const configPane = initConfigPane();
  const rulePane = initRulePane();
  const actionPane = new Pane({
    container: document.getElementById("action-container"),
    title: "Actions"
  });

  actionPane.addButton({
    title: "Run",
    label: "Calculate Signals",
  }).on("click", () => {
    const params = {
      source: getSource(),
      rules: JSON.stringify(getState(rulePane)),
      config: JSON.stringify(getState(configPane))
    };
    const url = new URL("/fetch", location.origin);
    url.search = new URLSearchParams(params).toString();
    console.log("Calculating...", params);
    fetch(url)
      .then(res => res.json())
      .then(json => {
        if (json.success) {
          chart.remove();
          document.body.dispatchEvent(new Event("parse:csv"));
        }
        else alert("Error: " + (json.error || "Unknown error"));
      })
      .catch(error => console.log(error));
  });

  actionPane.addButton({
    title: "Run",
    label: "Fetch and calculate Signals",
  });

  actionPane.addButton({
    title: "Run",
    label: "Restore default config",
  }).on("click", () => {
    localStorage.removeItem("tp_configPaneState");
    localStorage.removeItem("tp_rulePaneState");
    location.reload();
  });
}