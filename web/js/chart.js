'use strict';

import { createChart, CandlestickSeries, createSeriesMarkers, LineSeries, CrosshairMode } from 'lightweight-charts';
import Papa from 'papaparse';
import moment from 'moment';
import config from './config.js';
import Line from './line.js';
import '../scss/bootstrap.scss';

function has(obj, key) {
    return obj && obj[key] !== undefined && obj[key] !== null && obj[key] !== '' && obj[key] !== '-';
}

/**
 * Process CSV data to generate candlestick series, markers, and MA lines.
 * @param {Array<Object>} data - Array of row objects from CSV.
 * @returns {Object} { series, markers, ma_20, ma_50 }
 */
function processChartData(data) {
    const seriesObject = {
        candle: {
            series: [],
        },
        marker: {
            series: [],
        },
        line: {},
        rawMapping: {}
    }

    Object.keys(config.LineSeries).forEach(key => {
        seriesObject.line[key] = [];
    });

    data.forEach(row => {
        const date = new Date(row.start);
        // UTC+7
        date.setHours(date.getHours() + 7);
        const time = date.getTime();
        // Candlestick series
        seriesObject.candle.series.push({
            time,
            open: Number(row.open),
            high: Number(row.high),
            low: Number(row.low),
            close: Number(row.close),
            raw: row
        });
        // Markers
        if (has(row, 'position') || has(row, 'sensitive_position')) {
            let isLong;
            let color;

            if (has(row, 'position')) {
                isLong = Number(row.position) === 1;
                color = isLong ? '#4AFA9A' : '#FF4976';
            }

            if (has(row, 'sensitive_position')) {
                isLong = Number(row.sensitive_position) === 1;
                color = isLong ? '#FFFF00' : '#7C4DFF';
            }

            let price = isLong ? Number(row.low) : Number(row.high);

            seriesObject.marker.series.push({
                time,
                position: isLong ? 'belowBar' : 'aboveBar',
                color: color,
                shape: isLong ? 'arrowUp' : 'arrowDown',
                text: isLong ? `B: ${price}` : `S: ${price}`,
            });
        }
        // MA lines
        Object.keys(seriesObject.line).forEach(key => {
            if (row[key] !== undefined && row[key] !== null && row[key] !== '' && row[key] !== '-') {
                seriesObject.line[key].push({
                    time,
                    value: Number(row[key])
                });
            }
        });

        seriesObject.rawMapping[time] = row;
    });

    return seriesObject;
}

/**
 * Format a number to a fixed decimal string.
 * @param {number} value - The number to format.
 * @param {number} fixed - The number of decimal places.
 * @returns {string} - Formatted number as a string.
 */
function parseFixed(value, fixed) {
    var num = Number(value);
    return !isNaN(num) ? num.toFixed(fixed) : '';
}

/**
 * Create a tooltip element for displaying chart data.
 * @returns {HTMLElement} - A tooltip element for displaying chart data.
 */
function createTooltip() {
    const toolTip = document.createElement('div');
    toolTip.style = `width: auto; height: auto; position: absolute; display: none; padding: 8px; box-sizing: border-box; font-size: 11px; text-align: left; z-index: 1000; top: 12px; left: 12px; pointer-events: none; border: 1px solid; border-radius: 1px;`;
    toolTip.style.background = 'white';
    toolTip.style.color = 'black';
    toolTip.style.borderColor = 'rgba( 38, 166, 154, 1)';
    return toolTip;
}

/**
 * Create a line for the tooltip with label and value.
 * @param {string} label - The label for the line.
 * @param {string} value - The value for the line.
 * @param {string} color - The color for the line.
 * @return {string} - HTML string for the tooltip line.
 */
function createTooltipLine(label, value, style) {
    return `<div style="${style}">
            <span style="font-weight: bold;">${label ? label + ':' : ''}</span> ${value}
        </div>`;
}

/**
 * Return Fraction Digits based on source file
 * @returns {number} - Fraction Digits number
 */
function getFractionDigits() {
    if (window.source) {
        const sourceSplit = window.source.split('_');
        const symbol = String(sourceSplit[0]).toUpperCase();
        const config = {
            BTCUSDT: 2,
            ETHUSDT: 2,
            XRPUSDT: 2,
            XLMUSDT: 4,
            KAITOCUSDT: 3
        };
        return config[symbol] || 2;
    }
    return 2;
}

/**
 * Render the chart with candlestick series and markers.
 * @param {Array<Object>} series - Candlestick series data.
 * @param {Array<Object>} markers - Marker objects for positions.
 * @param {Object} rawMapping - Mapping of time to raw data.
 */
function createChartElement(data) {
    const { candle, marker, line, rawMapping } = processChartData(data);

    // Initialize chart options
    const fractionDigits = getFractionDigits();
    const visibleRange = {
        from: data.length - 100,
        to: data.length - 1
    };
    const chartOptions = {
        layout: {
            background: { color: '#1e1e1e' },
            textColor: '#D1D4DC',
        },
        grid: {
            vertLines: { color: '#2B2B43' },
            horzLines: { color: '#2B2B43' },
        },
        crosshair: {
            mode: CrosshairMode.Normal,
        },
        localization: {
            priceFormatter: price => {
                return `${parseFixed(price, fractionDigits)}$`;
            },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false
        }
    };
    const candlestickOptions = {
        upColor: '#4AFA9A',
        downColor: '#FF4976',
        borderUpColor: '#4AFA9A',
        borderDownColor: '#FF4976',
        wickUpColor: '#4AFA9A',
        wickDownColor: '#FF4976',
    };
    const defaultLineOptions = {
        lineWidth: 2
    };

    // Create chart container and chart instance
    const chartContainer = document.getElementById('chart-container');
    const chart = createChart(chartContainer, chartOptions);
    const candlestickSeries = chart.addSeries(CandlestickSeries, candlestickOptions);
    candlestickSeries.setData(candle.series);

    // Create markers for positions
    createSeriesMarkers(candlestickSeries, marker.series);

    // Create tooltip for displaying data
    const toolTip = createTooltip();
    chartContainer.appendChild(toolTip);

    chart.subscribeCrosshairMove(param => {
        if (
            param.point === undefined ||
            !param.time ||
            param.point.x < 0 ||
            param.point.x > chartContainer.clientWidth ||
            param.point.y < 0 ||
            param.point.y > chartContainer.clientHeight
        ) {
            toolTip.style.display = 'none';
        } else {
            const data = param.seriesData.get(candlestickSeries);
            const price = data.value !== undefined ? data.value : data.close;
            const dateStr = moment(param.time).format('YYYY-MM-DD HH:mm:ss');
            const time = Number(param.time);
            const rawData = rawMapping[time] || {};

            const toolTipLines = [
                createTooltipLine('', price, 'font-size: 16px; margin-bottom: 4px; color: black; font-weight: bold;'),
                createTooltipLine('Time+7', dateStr, 'margin-bottom: 2px; color: black;'),
                createTooltipLine('High', data.high, 'margin-bottom: 2px; color: black;'),
                createTooltipLine('Low', data.low, 'margin-bottom: 2px; color: black;'),
                createTooltipLine('RSI (6)', parseFixed(rawData.rsi_6, 2), 'margin-bottom: 2px; color: black;'),
                createTooltipLine('RSI high (6)', parseFixed(rawData.rsi_6_high, 2), 'margin-bottom: 2px; color: red;'),
                createTooltipLine('RSI low (6)', parseFixed(rawData.rsi_6_low, 2), 'margin-bottom: 2px; color: green;')
            ];

            toolTip.innerHTML = toolTipLines.join('');

            const y = param.point.y;
            const toolTipWidth = 80;
            const toolTipHeight = 80;
            const toolTipMargin = 15;
            let left = param.point.x + toolTipMargin;
            if (left > chartContainer.clientWidth - toolTipWidth) {
                left = param.point.x - toolTipMargin - toolTipWidth;
            }

            let top = y + toolTipMargin;
            if (top > chartContainer.clientHeight - toolTipHeight) {
                top = y - toolTipHeight - toolTipMargin;
            }
            toolTip.style.display = 'block';
            toolTip.style.left = left + 'px';
            toolTip.style.top = '1rem';
        }
    });

    // Add line series
    Object.keys(line).forEach(key => {
        const options = config.LineSeries[key] || {};
        const lineObj = new Line(chart, line[key], { ...defaultLineOptions, ...options }, `line-${key}`);
        lineObj.render();
    });

    chart.timeScale().setVisibleLogicalRange(visibleRange);
}

/**
 * Callback for PapaParse complete event.
 * @param {Object} results - PapaParse results object.
 */
function papaComplete(results) {
    const data = results.data;
    createChartElement(data);
}

/**
 * Initialize parsing on page load if a source parameter is present in the URL.
 */
function initParseOnLoad() {
    const url = new URL(location.href);
    const path = 'dist/file';
    const origin = location.origin;
    const source = url.searchParams.get('source');
    const chartTitle = document.getElementById('chartTitle');
    const csvPath = `${origin}/${path}/${source}`;

    if (source) {
        window.source = source;
        chartTitle.textContent = `${source}`;
        console.log('Loading CSV from:', csvPath);
        Papa.parse(csvPath, {
            download: true,
            complete: papaComplete,
            header: true,
            skipEmptyLines: true,
        });
    }
}

/**
 * Fetch data from a URL.
 * @param {string} url - The URL to fetch data from.
 * @returns {Promise<Object>} - A promise that resolves to the fetched data.
 */
async function startFetch(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

/**
 * Initialize the fetch button to start fetching data.
 */
function initFetchHandler() {
    document.getElementById('fetch-button').addEventListener('click', function (e) {
        e.preventDefault();
        this.disabled = true;
        this.classList.add('disabled');
        startFetch(this.href).then(data => {
            if (data && data.success === true) {
                window.location.reload();
            } else {
                this.disabled = false;
                this.classList.remove('disabled');
            }
        }).catch(error => {
            this.disabled = false;
        });
    });
}

/**
 * Initialize file input event and CSV parsing.
 */
(function () {
    initParseOnLoad();
    initFetchHandler();
})();
