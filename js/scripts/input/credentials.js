'use strict';

const path = require('path');
const cwd = process.cwd();
const credentials = require(path.join(cwd, 'js', 'config', 'credentials.json'));

/**
 * Return credentials object
 * @param {string} name - App name
 * @returns {Object} - credentials object
 */
const getCredentials = (name) => {
    return credentials[name];
};

/**
 * Return Binance credentials object
 * @returns {Object} - Binance credentials object
 */
const getBinanceCredentials = () => {
    return getCredentials('binance');
}

/**
 * Return Telegram credentials object
 * @returns {Object} - Telegram credentials object
 */
const getTelegramCredentials = () => {
    return getCredentials('telegram');
}

module.exports = {
    getCredentials,
    getBinanceCredentials,
    getTelegramCredentials
};
