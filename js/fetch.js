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
const csvFileName = `export_${moment().format('YYYYMMDDkkmmss')}_binance_${params.symbol}_${params.interval}.csv`;

/**
 * Export API to be used in other programming language
 * @param {Array} klineArray - Kline data array
 */
const exportAPI = (klineArray) => {
    const apiFolderPath = path.join(exportDirPath, 'api');

    !fs.existsSync(apiFolderPath) && fs.mkdirSync(apiFolderPath);

    const api = {
        fileName: csvFileName,
        filePath: path.join(exportDirPath, csvFileName),
        symbol: params.symbol,
        interval: params.interval,
    };

    if (Array.isArray(klineArray)) {
        api.now = klineArray[klineArray.length - 1];
    }

    fs.writeFileSync(
        path.join(apiFolderPath, 'fetch.json'),
        JSON.stringify(api, null, 4)
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
    let timeSlots;

    if (!program.back || program.back === '0' || program.back === 0) {
        timeSlots = utils.calcTimeSlot(
            (new Date()),
            frameCount,
            params.interval
        );
    } else {
        let start = new Date();
        let end = new Date();
        start.setDate(start.getDate() - Number(program.back));
        start.setHours(0);
        start.setMinutes(0);
        start.setSeconds(0);
        start.setMilliseconds(0);
        timeSlots = utils.calcTimeSlotByDate(
            start,
            end,
            params.interval
        );
    }

    for (let idx = 0; idx < timeSlots.length; idx++) {
        const slot = timeSlots[idx];

        params.startTime = slot.startTime;
        params.endTime = slot.endTime;

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

    klineArray.forEach(item => {
        csv.writeRow([
            params.symbol,
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

    exportAPI(klineArray);
})();
