'use strict';

import { createChart, CandlestickSeries, createSeriesMarkers, LineSeries } from 'lightweight-charts';
import Papa from 'papaparse';
import moment from 'moment';

/**
 * Convert CSV data to candlestick series format for Lightweight Charts.
 * @param {Array<Object>} data - Array of row objects from CSV.
 * @returns {Array<Object>} Array of candlestick bar objects.
 */
function createLineSeries(data) {
    return data.map(row => {
        return {
            time: (new Date(row.start)).getTime(),
            open: Number(row.open),
            high: Number(row.high),
            low: Number(row.low),
            close: Number(row.close),
            raw: row
        };
    });
}

/**
 * Create a value series from the data.
 * @param {Array<Object>} data - Array of row objects from CSV.
 * @param {string} column - The column name to extract values from.
 * @returns {Array<Object>} Array of objects with time and value properties.
 */
function createValueSeries(data, column) {
    return data.map(row => {
        return {
            time: (new Date(row.start)).getTime(),
            value: Number(row[column])
        };
    });
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
 * Create marker objects for chart positions (long/short).
 * @param {Array<Object>} data - Array of row objects from CSV.
 * @returns {Array<Object>} Array of marker objects.
 */
function createMarkers(data) {
    return data.map(row => {
        if (row.position === '-' || !row.position) return null;
        let isLong = Number(row.position) === 1;
        return {
            time: (new Date(row.start)).getTime(),
            position: isLong ? 'belowBar' : 'aboveBar',
            color: isLong ? 'green' : 'red',
            shape: isLong ? 'arrowUp' : 'arrowDown',
            text: isLong ? 'B' : 'S',
        };
    }).filter(marker => marker !== null);
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

function createTooltip() {
    const toolTip = document.createElement('div');
    toolTip.style = `width: auto; height: auto; position: absolute; display: none; padding: 8px; box-sizing: border-box; font-size: 10px; text-align: left; z-index: 1000; top: 12px; left: 12px; pointer-events: none; border: 1px solid; border-radius: 1px;`;
    toolTip.style.background = 'white';
    toolTip.style.color = 'black';
    toolTip.style.borderColor = 'rgba( 38, 166, 154, 1)';
    return toolTip;
}

/**
 * Render the chart with candlestick series and markers.
 * @param {Array<Object>} series - Candlestick series data.
 * @param {Array<Object>} markers - Marker objects for positions.
 * @param {Object} rawMapping - Mapping of time to raw data.
 */
function createChartElement(data) {
    const series = createLineSeries(data);
    const markers = createMarkers(data);
    const rawMapping = createRawMappingByTime(series);
    const ma20 = createValueSeries(data, 'ma_20');
    const ma50 = createValueSeries(data, 'ma_50');

    // console.log('Loading series:', series);
    // console.log('Loading markers:', markers);
    // console.log('Loading rawMapping:', rawMapping);

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
                return `${price.toFixed(4)}$`;
            },
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

            toolTip.innerHTML = `
            <div style="font-size: 16px; margin-bottom: 4px; color: ${'black'}">
            ${price}
            </div>
            <div style="margin-bottom: 2px;color: ${'black'}">
            Time: ${dateStr}
            </div>
            <div style="margin-bottom: 2px;color: ${'black'}">
            High: ${data.high}
            </div>
            <div style="margin-bottom: 2px;color: ${'black'}">
            Low: ${data.low}
            </div>
            <div style="margin-bottom: 2px;color: ${'black'}">
            RSI (6): ${parseFixed(rawData.rsi_6, 2)}
            </div>
            <div style="margin-bottom: 2px;color: ${'black'}">
            RSI of high (6): ${parseFixed(rawData.rsi_6_of_high, 2)}
            </div>
            <div style="margin-bottom: 2px;color: ${'black'}">
            RSI of low (6): ${parseFixed(rawData.rsi_6_of_low, 2)}
            </div>
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
            toolTip.style.top = top + 'px';
        }
    });

    const ma20LineSeries = chart.addSeries(LineSeries, { color: '#39e75f' });
    ma20LineSeries.setData(ma20);
    const ma50LineSeries = chart.addSeries(LineSeries, { color: '#f9c74f' });
    ma50LineSeries.setData(ma50);

    chart.timeScale().fitContent();
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
 * Initialize file input event and CSV parsing.
 */
(function () {
    // document.getElementById('fileInput').addEventListener('change', function (e) {
    //     const file = e.target.files[0];
    //     Papa.parse(file, {
    //         complete: papaComplete,
    //         header: true,
    //         skipEmptyLines: true,
    //     });
    // });

    const host = 'http://127.0.0.1:5500/web/dist/file';
    const url = new URL(location.href);
    const searchParams = url.searchParams;
    const source = searchParams.get('source');
    const chartTitle = document.getElementById('chart-title');

    if (!source) return;

    chartTitle.textContent = `Backtest Chart: ${source}`;

    Papa.parse(`${host}/${source}`, {
        download: true,
        complete: papaComplete,
        header: true,
        skipEmptyLines: true,
    })
})();
