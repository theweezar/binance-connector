'use strict';

/** Packages */
const binance = require('binance');
const path = require('path');
const fs = require('fs');

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
        'date',
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
            item.date,
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

    if (fs.existsSync(exportFilePath)) {
        console.log(`Removing existing file: ${exportFilePath}`);
        fs.unlinkSync(exportFilePath);
    }

    csv.export();
}

/**
 * Calculate time slots based on options
 * @param {Object} opts - Options for calculating time slots
 * @returns {Array} - Array of time slots
 */
function calcTimeSlot(opts) {
    const backDate = Number(opts.back);

    if (opts.mode === 'frame') {
        return utils.calcTimeSlot((new Date()), Number(opts.frame), opts.interval);
    }

    if (opts.mode === 'date') {
        let start = new Date();
        start.setDate(start.getDate() - backDate);
        start.setHours(0, 0, 0, 0);
        return utils.calcTimeSlotByDate(start, (new Date()), opts.interval);
    }

    if (opts.mode === 'period') {
        let start = new Date(opts.start);
        let end = new Date(opts.end);
        return utils.calcTimeSlotByDate(start, end, opts.interval);
    }

    throw Error('Cannot parse time slots');
}

/**
 * Validate the options provided
 * @param {Object} opts - Options to validate
 */
function validate(opts) {
    if (!opts.symbol) this.missingArgument('symbol');
    if (!opts.interval) this.missingArgument('interval');
    if (opts.mode === 'frame' && (!opts.frame || !Number(opts.frame) || Number(opts.frame) === 0)) {
        console.error('error: missing or invalid frame number');
        process.exit(1);
    }
    if (opts.mode === 'period') {
        if (!opts.start) this.missingArgument('start');
        if (!opts.end) this.missingArgument('end');
        if ((new Date(opts.start)).toString().toLowerCase() === 'invalid date') {
            console.error('error: invalid start date');
            process.exit(1);
        }
        if ((new Date(opts.end)).toString().toLowerCase() === 'invalid date') {
            console.error('error: invalid end date');
            process.exit(1);
        }
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
    const exportFilePath = path.join(cwd, opts.path);

    console.log(`Fetching data with ${timeSlots.length} time slots`);

    const data = await fetchData(key, timeSlots, params);

    exportCSV(data, exportFilePath, params.symbol);

    exportAPI(data, exportFilePath, params);
}

/**
 * Execute the process using frame mode
 * @param {Object} opts - Options for execution
 */
function executeUsingFrame(opts) {
    const options = {
        mode: 'frame'
    };
    Object.assign(options, opts);
    validate.call(this, options)
    execute.call(this, options)
}

/**
 * Execute the process using date mode
 * @param {Object} opts - Options for execution
 */
function executeUsingDate(opts) {
    const options = {
        mode: 'date'
    };
    Object.assign(options, opts);
    validate.call(this, options)
    execute.call(this, options)
}

/**
 * Execute the process using period mode
 * @param {Object} opts - Options for execution
 */
function executeUsingPeriod(opts) {
    const options = {
        mode: 'period'
    };
    Object.assign(options, opts);
    validate.call(this, options)
    execute.call(this, options)
}

module.exports = {
    execute,
    executeUsingFrame,
    executeUsingDate,
    executeUsingPeriod
};
