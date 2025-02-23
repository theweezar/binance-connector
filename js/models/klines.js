'use strict';

const { parseTimeString } = require('../scripts/utils');

/**
 * @constructor
 * 
 * @param {Array|null|undefined} apiResponseArray - API response array
 */
function klinesModel(apiResponseArray) {
    this.klines = [];

    if (Array.isArray(apiResponseArray)) {
        apiResponseArray.forEach(item => {
            let kline = {
                openTime: parseTimeString(item[0]),
                openPrice: item[1],
                highPrice: item[2],
                lowPrice: item[3],
                closePrice: item[4],
                volume: item[5],
                closeTime: parseTimeString(item[6]),

                // Up/Down
                type: item[4] - item[1] >= 0 ? 'U' : 'D'
            };

            this.klines.push(kline);
        });
    }
}

/**
 * Export klines array
 * @returns {Array} - klines array
 */
klinesModel.prototype.export = function () {
    return this.klines;
};

/**
 * Append another klines model
 * @param {klinesModel} klines - klines model
 */
klinesModel.prototype.push = function (klines) {
    this.klines = this.klines.concat(klines.export());
}

/**
 * Unshift another klines model
 * @param {klinesModel} klines - klines model
 */
klinesModel.prototype.unshift = function (klines) {
    this.klines = klines.export().concat(this.klines);
}

module.exports = klinesModel;
