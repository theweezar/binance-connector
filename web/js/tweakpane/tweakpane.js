"use strict";

import { Pane } from "tweakpane";
import { getSource, getSourceObject } from "../utils/url";
import cfgPaneJson from "./configpane.json";
import rulePaneJson from "./rulepane.json";

/**
 * Utility functions for localStorage state management
 */
const StateManager = {
  save: (stateName, state) => {
    try {
      localStorage.setItem(stateName, JSON.stringify(state));
    } catch (error) {
      console.error("Error saving state:", error);
    }
  },

  load: (stateName) => {
    try {
      const state = localStorage.getItem(stateName);
      return state ? JSON.parse(state) : null;
    } catch (error) {
      console.error("Error loading state:", error);
      return null;
    }
  },

  remove: (stateName) => {
    try {
      localStorage.removeItem(stateName);
    } catch (error) {
      console.error("Error removing state:", error);
    }
  }
};

const StateCollector = {
  collectPaneState: function (state) {
    const children = Array.isArray(state.children) ? state.children : [];
    const entries = children.flatMap(folderState =>
      Array.isArray(folderState.children)
        ? folderState.children.map(bindingEl => [
          bindingEl.binding.key,
          bindingEl.binding.value
        ]) : []
    );
    return Object.fromEntries(entries);
  },
  collectFolderState: function (folderState) {
    const entries = Array.isArray(folderState.children)
      ? folderState.children.map(bindingEl => [
        bindingEl.binding.key,
        bindingEl.binding.value
      ]) : [];
    return Object.fromEntries(entries);
  }
};

/**
 * Base Pane class following OOP principles
 */
class BasePane {
  constructor(containerId, title, jsonConfig, stateKey) {
    this.containerId = containerId;
    this.title = title;
    this.jsonConfig = jsonConfig;
    this.stateKey = stateKey;
    this.config = {};
    this.pane = null;

    this.init();
  }

  init() {
    this.createConfigObject();
    this.createPane();
    this.setupBindings();
    this.setupStateManagement();
  }

  createConfigObject() {
    this.jsonConfig.forEach(section => {
      (section.params || []).forEach(param => {
        this.config[param.label] = param.value;
      });
    });
  }

  createPane() {
    this.pane = new Pane({
      container: document.getElementById(this.containerId),
      title: this.title
    });
  }

  setupBindings() {
    this.jsonConfig.forEach(section => {
      const folder = this.pane.addFolder({ title: section.folder });
      (section.params || []).forEach(param => {
        const label = param.title || param.label;
        folder.addBinding(this.config, param.label, { label });
      });
    });
  }

  setupStateManagement() {
    this.pane.on("change", () => {
      StateManager.save(this.stateKey, this.pane.exportState());
    });

    const savedState = StateManager.load(this.stateKey);
    this.import(savedState);
  }

  import(state) {
    if (state) {
      try {
        this.pane.importState(state);
      } catch (error) {
        console.error("Error importing pane state:", error);
      }
    }
  }

  getState() {
    return StateCollector.collectPaneState(this.pane.exportState());
  }
}

/**
 * Action Pane for user interactions
 */
class ActionPane {
  constructor(containerId, configPane, rulePane) {
    this.containerId = containerId;
    this.configPane = configPane;
    this.rulePane = rulePane;
    this.pane = null;

    this.init();
  }

  init() {
    this.createPane();
    this.setupActions();
  }

  createPane() {
    this.pane = new Pane({
      container: document.getElementById(this.containerId),
      title: "Actions"
    });
  }

  setupActions() {
    this.addCalculateSignalsButton();
    this.addRestoreDefaultsButton();
    this.addFetchAndCalculateButton();
  }

  addCalculateSignalsButton() {
    this.pane.addButton({
      title: "Run",
      label: "Calculate Signals",
    }).on("click", () => this.handleCalculateSignals());
  }

  addFetchAndCalculateButton() {
    const cfg = getSourceObject();
    const folder = this.pane.addFolder({ title: "Fetch/Calculate Signals" });
    folder.addBinding(cfg, "symbol", { label: "Symbol" });
    folder.addBinding(cfg, "interval", { label: "Interval" });

    this.pane.addButton({
      title: "Run"
    }).on("click", () => {
      const symbolParams = StateCollector.collectFolderState(folder.exportState());
      const source = `${symbolParams.symbol}_${symbolParams.interval}.csv`;
      const params = {
        source,
        rules: JSON.stringify(this.rulePane.getState()),
        config: JSON.stringify(this.configPane.getState()),
        ...symbolParams
      };
      const url = new URL("/fetch", location.origin);
      url.search = new URLSearchParams(params).toString();
      fetch(url)
        .then(res => res.json())
        .then(json => {
          if (json.success) {
            location.search = new URLSearchParams({ source }).toString();
          }
        })
        .catch(error => console.log("Fetch error:", error));
    });
  }

  addRestoreDefaultsButton() {
    this.pane.addButton({
      title: "Run",
      label: "Restore Default",
    }).on("click", () => this.handleRestoreDefaults());
  }

  handleCalculateSignals() {
    const params = {
      source: getSource(),
      rules: JSON.stringify(this.rulePane.getState()),
      config: JSON.stringify(this.configPane.getState())
    };

    const url = new URL("/fetch", location.origin);
    url.search = new URLSearchParams(params).toString();

    fetch(url)
      .then(res => res.json())
      .then(json => this.handleCalculateResponse(json))
      .catch(error => console.log("Fetch error:", error));
  }

  handleCalculateResponse(json) {
    if (json.success) {
      chart.remove();
      document.body.dispatchEvent(new Event("parse:csv"));
    } else {
      alert("Error: " + (json.error || "Unknown error"));
    }
  }

  handleRestoreDefaults() {
    StateManager.remove("tp_configPaneState");
    StateManager.remove("tp_rulePaneState");
    location.reload();
  }
}

/**
 * UI utility functions
 */
const UIHelper = {
  adjustHeight: () => {
    const tabWrapperEl = document.getElementById("myTab");
    const settingTabEl = document.getElementById("settings");
    const validHeight = window.innerHeight - tabWrapperEl.clientHeight - 8;

    settingTabEl.style.height = `${validHeight}px`;
    settingTabEl.style.overflowY = "scroll";
  }
};

/**
 * Main initialization function
 */
export function init() {
  UIHelper.adjustHeight();

  const configPane = new BasePane("tweakpane-container", "Settings", cfgPaneJson, "tp_configPaneState");
  const rulePane = new BasePane("rulepane-container", "Trading Rules", rulePaneJson, "tp_rulePaneState");
  const actionPane = new ActionPane("action-container", configPane, rulePane);

  return { configPane, rulePane, actionPane };
}