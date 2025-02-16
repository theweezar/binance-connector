'use strict';

/** Packages */
const binance = require('binance');
const path = require('path');
const shell = require('shelljs');
const fs = require('fs');
const moment = require('moment');

/** Scripts, variables */
const symbol = require('./config/symbol.json');
const credentials = require('./scripts/input/credentials');
const Klines = require('./models/klines');
const CSV = require('./scripts/csv');
const program = require('./scripts/input/prompt');
const utils = require('./scripts/utils');

/** Define global variables */
const key = credentials.getBinanceCredentials();
const cwd = process.cwd();
const exportDirPath = path.join(cwd, program.path);
const frameCount = Number(program.frame);
const selectedSymbol = symbol[program.symbol];
const params = {
    symbol: selectedSymbol,
    interval: program.interval
};
const date = moment().format('YYYYMMDDkkmmss');
const csvFileName = `export_${date}_binance_${params.symbol}_${params.interval}.csv`;

/**
 * Export API to be used in other programming language
 * @param {Array} klineArray - Kline data array
 */
const exportLastestAPI = (klineArray) => {
    const apiFolderPath = path.join(exportDirPath, 'api');

    !fs.existsSync(apiFolderPath) && fs.mkdirSync(apiFolderPath);

    const exportObj = {
        fileName: csvFileName,
        filePath: path.join(exportDirPath, csvFileName),
        symbol: params.symbol,
        interval: params.interval,
    };

    if (Array.isArray(klineArray)) {
        exportObj.lastestPrice = klineArray[klineArray.length - 1];
    }

    fs.writeFileSync(
        path.join(apiFolderPath, 'fetch.json'),
        JSON.stringify(exportObj, null, 4)
    );
}

/**
 * Fetching data
 * @returns {Array} - Kline data array
 */
const fetchData = async () => {
    const client = new binance.USDMClient({
        api_key: key.apiKey,
        api_secret: key.secretKey
    });

    const mainKlineModel = new Klines();

    const timeSlots = utils.calcTimeSlot(
        (new Date()),
        frameCount,
        params.interval
    );

    for (let idx = 0; idx < timeSlots.length; idx++) {
        const slot = timeSlots[idx];

        if (timeSlots.length > 1) {
            params.startTime = slot.startTime;
            params.endTime = slot.endTime;
        }

        // https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/Kline-Candlestick-Data
        const klineData = await client.getKlines(params).catch(error => {
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

(async () => {
    const klineArray = await fetchData();

    const csv = new CSV({
        path: exportDirPath,
        fileName: csvFileName
    });

    csv.writeHeader([
        'Symbol',
        'Open Time',
        'Close Time',
        'Open',
        'High',
        'Low',
        'Close',
        'Volume',
        'Type'
    ]);

    klineArray.forEach(item => {
        csv.writeRow([
            params.symbol,
            item.openTime,
            item.closeTime,
            item.openPrice,
            item.highPrice,
            item.lowPrice,
            item.closePrice,
            item.volume,
            item.type
        ]);
    });

    shell.ls(`${exportDirPath}/*.csv`).forEach(function (file) {
        shell.rm('-f', file);
    });

    csv.export();

    exportLastestAPI(klineArray);
})();
