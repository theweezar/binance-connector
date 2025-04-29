'use strict';

const { parseTimeString, parseDateString } = require('../scripts/utils');

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
                start: parseTimeString(item[0]),
                open: item[1],
                high: item[2],
                low: item[3],
                close: item[4],
                vol: item[5],
                end: parseTimeString(item[6]),

                // Up/Down
                type: item[4] - item[1] >= 0 ? 'U' : 'D',
                date: parseDateString(item[0]),
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
