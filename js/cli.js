'use strict';

const program = require('commander');
const f = require('./lib/fetch');

// node ./js/cli.js price:frame -s "BTC" -i "15m" -f 1
program
    .command('price:frame')
    .option('-p, --path [export-path]', 'Configure export folder path', 'ignore')
    .option('-s, --symbol [type]', 'Configure coin symbol')
    .option('-i, --interval [type]', 'Configure chart interval')
    .option('-f, --frame [type]', 'Configure how many frame to loop')
    .description('Fetch price from Binance by frame')
    .action(f.executeUsingFrame);

// node ./js/cli.js price:date -s "BTC" -i "15m" -b 1
program
    .command('price:date')
    .option('-p, --path [export-path]', 'Configure export folder path', 'ignore')
    .option('-s, --symbol [type]', 'Configure coin symbol')
    .option('-i, --interval [type]', 'Configure chart interval')
    .option('-b, --back [type]', 'Configure the start time to current time')
    .description('Fetch price from Binance by date')
    .action(f.executeUsingDate);

// node ./js/cli.js price:period -s "BTC" -i "15m" -S "2025-01-01" -E "2025-03-24"
program
    .command('price:period')
    .option('-p, --path [export-path]', 'Configure export folder path', 'ignore')
    .option('-s, --symbol [type]', 'Configure coin symbol')
    .option('-i, --interval [type]', 'Configure chart interval')
    .option('-S, --start [date]', 'Start date')
    .option('-E, --end [date]', 'End date')
    .description('Fetch price from Binance by period')
    .action(f.executeUsingPeriod);

program.parse(process.argv);
