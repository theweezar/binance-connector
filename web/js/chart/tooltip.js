// src/ui/tooltip.js
'use strict';

export function createTooltip() {
  const toolTip = document.createElement('div');
  Object.assign(toolTip.style, {
    width: 'auto',
    height: 'auto',
    position: 'absolute',
    display: 'none',
    padding: '8px',
    boxSizing: 'border-box',
    fontSize: '11px',
    textAlign: 'left',
    zIndex: '1000',
    top: '12px',
    left: '12px',
    pointerEvents: 'none',
    border: '1px solid rgba(38, 166, 154, 1)',
    borderRadius: '1px',
    background: 'white',
    color: 'black',
  });
  return toolTip;
}

export function createTooltipLine(label, value, style = '') {
  return `
        <div style="${style}">
            <span style="font-weight: bold;">${label ? label + ':' : ''}</span> ${value}
        </div>
    `;
}
