'use strict';

const program = require('commander');

module.exports = (() => {
    /** Create prompt for script */
    program.version('0.1.0')
        .option('-p, --path [export-path]', 'Configure export folder path', 'ignore')
        .option('-s, --symbol [type]', 'Configure coin symbol', 'BTC')
        .option('-i, --interval [type]', 'Configure chart interval', '1h')
        .option('-f, --frame [type]', 'Configure how many frame to loop', 1)
        .option('-b, --back [type]', 'Configure the start time to current time')
        .parse(process.argv);

    return {
        path: program.path,
        frame: program.frame,
        interval: program.interval,
        symbol: program.symbol,
        back: program.back
    };
})();
