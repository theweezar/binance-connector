'use strict';

const fs = require('fs');
const path = require('path');

/**
 * @constructor
 * 
 * @param {Object} option - Option object
 */
function csv(option) {
    this.header = [];
    this.rows = [];
    this.length = 0;
    this.path = option.path;
    this.fileName = option.fileName || 'export.csv';
    this.delimeter = option.delimeter || ',';
}

/**
 * Set file name
 * @param {string} fileName - File name
 */
csv.prototype.setFileName = function (fileName) {
    this.fileName = fileName;
};

/**
 * Write header;
 * @param {Array} header - Array of header string
 */
csv.prototype.writeHeader = function (header) {
    if (this.header.length === 0) {
        this.header.push(header.join(this.delimeter));
    } else {
        this.header[0] = header.join(this.delimeter);
    }
};

/**
 * Write rows;
 * @param {Array} data - Array of data
 */
csv.prototype.writeRow = function (data) {
    this.rows.push(data.join(this.delimeter));
    this.length++;
};

/**
 * Export CSV file to directory
 */
csv.prototype.export = function () {
    if (!this.path) {
        throw new Error('CSV file path not found.');
    }

    let exportArr = [];
    let finalPath = path.join(this.path, this.fileName);

    if (this.header.length) {
        exportArr.push(this.header.pop());
    }

    exportArr = exportArr.concat(this.rows);

    // Create folder if not exist
    if (!fs.existsSync(this.path)) {
        fs.mkdirSync(this.path);
    }

    // Write CSV file
    fs.writeFileSync(finalPath, exportArr.join('\n'));
    console.log(`Exported file in ${finalPath}`);
};

module.exports = csv;
