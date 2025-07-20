'use strict';

import { createChart, CandlestickSeries, createSeriesMarkers, LineSeries } from 'lightweight-charts';
import Papa from 'papaparse';
import moment from 'moment';
import '../scss/bootstrap.scss';

/**
 * Process CSV data to generate candlestick series, markers, and MA lines.
 * @param {Array<Object>} data - Array of row objects from CSV.
 * @returns {Object} { series, markers, ma20, ma50 }
 */
function processChartData(data) {
    const series = [];
    const markers = [];
    const ma20 = [];
    const ma50 = [];
    data.forEach(row => {
        const date = new Date(row.start);
        // UTC+7
        date.setHours(date.getHours() + 7);
        const time = date.getTime();
        // Candlestick series
        series.push({
            time,
            open: Number(row.open),
            high: Number(row.high),
            low: Number(row.low),
            close: Number(row.close),
            raw: row
        });
        // Markers
        if (row.position !== '-' && row.position !== undefined && row.position !== null && row.position !== '') {
            let isLong = Number(row.position) === 1;
            markers.push({
                time,
                position: isLong ? 'belowBar' : 'aboveBar',
                color: isLong ? 'green' : 'red',
                shape: isLong ? 'arrowUp' : 'arrowDown',
                text: isLong ? 'B' : 'S',
            });
        }
        // MA lines
        ma20.push({
            time,
            value: Number(row.ma_20)
        });
        ma50.push({
            time,
            value: Number(row.ma_50)
        });
    });
    return { series, markers, ma20, ma50 };
}

/**
 * Create a mapping of raw data by time.
 * @param {Array<Object>} series - Candlestick series data.
 * @returns {Object} Mapping of time to raw data.
 */
function createRawMappingByTime(series) {
    const rawMapping = {};
    series.forEach(bar => {
        rawMapping[bar.time] = bar.raw;
    });
    return rawMapping;
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

function createTooltipLine(label, value, color = 'black') {
    return `<div style="margin-bottom: 2px;color: ${color}">
            <span style="font-weight: bold;">${label}:</span> ${value}
        </div>`;
}

/**
 * Return Fraction Digits based on source file
 * @returns {number} - Fraction Digits number
 */
function getFractionDigits() {
    if (window.source) {
        let sourceSplit = window.source.split('_');
        let symbol = String(sourceSplit[0]).toUpperCase();
        let config = {
            BTCUSDT: 2,
            ETHUSDT: 2,
            XRPUSDT: 2,
            XLMUSDT: 4,
            KAITOCUSDT: 3
        };
        return config[symbol] || 0;
    }
    return 0;
}

/**
 * Render the chart with candlestick series and markers.
 * @param {Array<Object>} series - Candlestick series data.
 * @param {Array<Object>} markers - Marker objects for positions.
 * @param {Object} rawMapping - Mapping of time to raw data.
 */
function createChartElement(data) {
    const { series, markers, ma20, ma50 } = processChartData(data);
    const rawMapping = createRawMappingByTime(series);
    const fractionDigits = getFractionDigits();
    const visibleRange = {
        from: data.length - 100,
        to: data.length - 1
    };

    console.log('Loading series:', series);
    console.log('Loading markers:', markers);
    console.log('Loading rawMapping:', rawMapping);

    const chartOptions = {
        layout: {
            textColor: 'black',
            background: {
                type: 'solid',
                color: 'white'
            }
        },
        grid: {
            vertLines: { color: "transparent" },
            horzLines: { color: "transparent" },
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
    const chartContainer = document.getElementById('chart-container');
    const chart = createChart(chartContainer, chartOptions);
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350'
    });
    candlestickSeries.setData(series);
    createSeriesMarkers(candlestickSeries, markers);

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
            const toolTipWidth = 80;
            const toolTipHeight = 80;
            const toolTipMargin = 15;
            const data = param.seriesData.get(candlestickSeries);
            const price = data.value !== undefined ? data.value : data.close;
            const dateStr = moment(param.time).format('YYYY-MM-DD HH:mm:ss');
            const time = Number(param.time);
            const rawData = rawMapping[time] || {};

            const toolTipLines = [
                createTooltipLine('Time', dateStr),
                createTooltipLine('High', data.high),
                createTooltipLine('Low', data.low),
                createTooltipLine('RSI (6)', parseFixed(rawData.rsi_6, 2)),
                createTooltipLine('RSI high (6)', parseFixed(rawData.rsi_6_of_high, 2), 'red'),
                createTooltipLine('RSI low (6)', parseFixed(rawData.rsi_6_of_low, 2), 'green')
            ];

            toolTip.innerHTML = `
            <div style="font-size: 16px; margin-bottom: 4px; color: ${'black'}">
            ${price}
            </div>
            ${toolTipLines.join('')}
            `;

            toolTip.style.display = 'block';
            const y = param.point.y;
            let left = param.point.x + toolTipMargin;
            if (left > chartContainer.clientWidth - toolTipWidth) {
                left = param.point.x - toolTipMargin - toolTipWidth;
            }

            let top = y + toolTipMargin;
            if (top > chartContainer.clientHeight - toolTipHeight) {
                top = y - toolTipHeight - toolTipMargin;
            }
            toolTip.style.left = left + 'px';
            toolTip.style.top = '1rem';
        }
    });

    const ma20LineSeries = chart.addSeries(LineSeries, { color: '#39e75f' });
    ma20LineSeries.setData(ma20);
    const ma50LineSeries = chart.addSeries(LineSeries, { color: '#f9c74f' });
    ma50LineSeries.setData(ma50);

    // chart.timeScale().fitContent();
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

function parseOnFileInput() {
    document.getElementById('fileInput').addEventListener('change', function (e) {
        const file = e.target.files[0];
        Papa.parse(file, {
            complete: papaComplete,
            header: true,
            skipEmptyLines: true,
        });
    });
}

/**
 * Initialize parsing on page load if a source parameter is present in the URL.
 */
function initParseOnLoad() {
    const url = new URL(location.href);
    const path = 'dist/file';
    const origin = location.origin;
    const source = url.searchParams.get('source');
    const chartTitle = document.getElementById('chart-title');
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
