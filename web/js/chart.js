'use strict';

require('../dist/js/lightweight-charts.standalone.production.js');

const Papa = require('papaparse');

/**
 * Convert CSV data to candlestick series format for Lightweight Charts.
 * @param {Array<Object>} data - Array of row objects from CSV.
 * @returns {Array<Object>} Array of candlestick bar objects.
 */
function createLineSeries(data) {
    return data.map(row => {
        return {
            time: (new Date(row.start)).getTime(),
            open: row.open,
            high: row.high,
            low: row.low,
            close: row.close
        };
    });
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
            text: `RSI(6): ${row.rsi_6}`
        };
    }).filter(marker => marker !== null);
}

/**
 * Render the chart with candlestick series and markers.
 * @param {Array<Object>} series - Candlestick series data.
 * @param {Array<Object>} markers - Marker objects for positions.
 */
function createChartElement(series, markers) {

    console.log('Loading series:', series);
    console.log('Loading markers:', markers);

    const chartOptions = {
        layout: {
            textColor: 'black',
            background: {
                type: 'solid',
                color: 'white'
            }
        }
    };
    const chart = LightweightCharts.createChart(document.getElementById('chart-container'), chartOptions);
    const candlestickSeries = chart.addSeries(LightweightCharts.CandlestickSeries, {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350'
    });

    candlestickSeries.setData(series);
    LightweightCharts.createSeriesMarkers(candlestickSeries, markers);
    chart.timeScale().fitContent();
}

/**
 * Callback for PapaParse complete event.
 * @param {Object} results - PapaParse results object.
 */
function papaComplete(results) {
    const data = results.data;
    const lineSeries = createLineSeries(data);
    const markers = createMarkers(data);
    createChartElement(lineSeries, markers);
}

/**
 * Initialize file input event and CSV parsing.
 */
(function () {
    document.getElementById('fileInput').addEventListener('change', function (e) {
        const file = e.target.files[0];
        Papa.parse(file, {
            complete: papaComplete,
            header: true,
            skipEmptyLines: true,
        });
    });
})();
