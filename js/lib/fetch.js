'use strict';

/** Packages */
const binance = require('binance');
const path = require('path');
const shell = require('shelljs');
const fs = require('fs');
const moment = require('moment');

/** Scripts, variables */
const symbol = require('../config/symbol.json');
const credentials = require('../scripts/input/credentials');
const Klines = require('../models/klines');
const CSV = require('../scripts/csv');
const utils = require('../scripts/utils');

/**
 * Export API to be used in other programming language
 * @param {Array} data - Data array
 * @param {string} exportFilePath - Path to the export file
 * @param {Object} additional - Additional parameters to include in the API
 */
function exportAPI(data, exportFilePath, additional) {
    const split = exportFilePath.split('\\');
    const fileName = split.pop();
    const exportDirPath = split.join('\\');
    const apiFolderPath = path.join(exportDirPath, 'api');

    if (!fs.existsSync(apiFolderPath)) fs.mkdirSync(apiFolderPath);

    const api = {
        fileName: fileName,
        filePath: exportFilePath
    };

    Object.assign(api, additional);

    if (Array.isArray(data)) {
        api.now = data[data.length - 1];
    }

    fs.writeFileSync(
        path.join(apiFolderPath, 'fetch.json'),
        JSON.stringify(api, null, 4)
    );
}

/**
 * Fetching data
 * @param {Object} key - Binance API credentials
 * @param {Array} timeSlots - Array of time slots
 * @param {Object} params - Parameters for fetching data
 * @returns {Array} - Kline data array
 */
async function fetchData(key, timeSlots, params) {
    const client = new binance.USDMClient({
        api_key: key.apiKey,
        api_secret: key.secretKey
    });
    const mainKlineModel = new Klines();
    const _params = JSON.parse(JSON.stringify(params));

    for (let idx = 0; idx < timeSlots.length; idx++) {
        const slot = timeSlots[idx];

        _params.startTime = slot.startTime;
        _params.endTime = slot.endTime;

        // https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/Kline-Candlestick-Data
        const klineData = await client.getKlines(_params).catch(error => {
            console.error(error);
        });

        if (klineData) {
            const klines = new Klines(klineData);
            mainKlineModel.unshift(klines);
        }

        await utils.sleep(250);
    }

    return mainKlineModel.export();
};

/**
 * Export data to CSV file
 * @param {Array} data - Data array
 * @param {string} exportFilePath - Path to the export file
 * @param {string} symbol - Trading symbol
 */
function exportCSV(data, exportFilePath, symbol) {
    const split = exportFilePath.split('\\');
    const fileName = split.pop();
    const exportDirPath = split.join('\\');

    const csv = new CSV({
        path: exportDirPath,
        fileName: fileName
    });

    csv.writeHeader([
        'symbol',
        'start',
        'end',
        'open',
        'high',
        'low',
        'close',
        'vol',
        'type'
    ]);

    data.forEach(item => {
        csv.writeRow([
            symbol,
            item.start,
            item.end,
            item.open,
            item.high,
            item.low,
            item.close,
            item.vol,
            item.type
        ]);
    });

    shell.ls(`${exportDirPath}/*.csv`).forEach(function (file) {
        shell.rm('-f', file);
    });

    csv.export();
}

/**
 * Calculate time slots based on options
 * @param {Object} opts - Options for calculating time slots
 * @returns {Array} - Array of time slots
 */
function calcTimeSlot(opts) {
    const backDate = Number(opts.back);

    if (!backDate || isNaN(backDate)) {
        return utils.calcTimeSlot((new Date()), Number(opts.frame), opts.interval);
    } else {
        let start = new Date();
        start.setDate(start.getDate() - backDate);
        start.setHours(0, 0, 0, 0);
        return utils.calcTimeSlotByDate(start, (new Date()), opts.interval);
    }
}

/**
 * Execute the data fetching and exporting process
 * @param {Object} opts - Options for execution
 */
async function execute(opts) {
    const key = credentials.getBinanceCredentials();
    const timeSlots = calcTimeSlot(opts);
    const selectedSymbol = symbol[opts.symbol];
    const params = {
        symbol: selectedSymbol,
        interval: opts.interval
    };
    const cwd = process.cwd();
    const csvFileName = `export_${moment().format('YYYYMMDDkkmmss')}_binance_${params.symbol}_${params.interval}.csv`;
    const exportFilePath = path.join(cwd, opts.path, csvFileName);
    const data = await fetchData(key, timeSlots, params);

    exportCSV(data, exportFilePath, params.symbol);

    exportAPI(data, exportFilePath, params);
}

module.exports = {
    execute
};
