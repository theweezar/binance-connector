'use strict';

const program = require('commander');
const f = require('./lib/fetch');

program
    .command('price:frame')
    .option('-p, --path [export-path]', 'Configure export folder path', 'ignore')
    .option('-s, --symbol [type]', 'Configure coin symbol', 'BTC')
    .option('-i, --interval [type]', 'Configure chart interval', '1h')
    .option('-f, --frame [type]', 'Configure how many frame to loop', 1)
    .option('-b, --back [type]', 'Configure the start time to current time')
    .description('Fetch price from Binance')
    .action(f.execute);

program.parse(process.argv);
