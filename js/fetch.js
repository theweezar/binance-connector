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

/** Check credentials */
const key = credentials.getBinanceCredentials();

const program = require('./scripts/input/prompt');

/** Define global variables */
const cwd = process.cwd();
const exportDirPath = path.join(cwd, program.path);
const frameCount = Number(program.frame);
const LIMIT = 500;
const timeSlots = (() => {
    const slots = [];
    const intervalMS = {
        '1m': 60000,
        '3m': 180000,
        '5m': 300000,
        '15m': 300000 * 3,
        '30m': 300000 * 6,
        '1h': 900000 * 4,
        '4h': 900000 * 16,
        '8h': 900000 * 32
    };
    const range = intervalMS[program.interval] * LIMIT;
    let end = (new Date()).getTime();

    for (let i = 0; i < frameCount; i++) {
        let start = end - range;
        slots.push({
            startTime: start,
            endTime: end
        });
        end = start;
    }

    return slots;
})();

const selectedSymbol = symbol[program.symbol];
const params = {
    symbol: selectedSymbol,
    interval: program.interval
};
const date = moment().format('YYYYMMDDkkmmss');
const csvFileName = `export_${date}_binance_${params.symbol}_${params.interval}.csv`;

const sleep = async (milliseconds) => {
    await new Promise(resolve => setTimeout(resolve, milliseconds));
}

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
        JSON.stringify(exportObj, null , 4)
    );
}

(async () => {
    const client = new binance.USDMClient({
        api_key: key.apiKey,
        api_secret: key.secretKey
    });

    const mainKlineModel = new Klines();

    for (let idx = 0; idx < frameCount; idx++) {
        const slot = timeSlots[idx];

        if (frameCount > 1) {
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

        await sleep(250);
    }

    const csv = new CSV({
        path: exportDirPath,
        fileName: csvFileName
    });

    const klineArray = mainKlineModel.export();

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

    if (program.deleteBeforeExport) {
        shell.ls(`${exportDirPath}/*.csv`).forEach(function (file) {
            shell.rm('-f', file);
        });
    }

    csv.export();

    exportLastestAPI(klineArray);

    console.info('Last price:', klineArray[klineArray.length - 1]);
})();
