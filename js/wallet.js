'use strict';

/** Packages */
const binance = require('binance');
const credentials = require('./scripts/input/credentials');

/** Check credentials */
const key = credentials.getBinanceCredentials();

(async () => {
    const client = new binance.MainClient({
        api_key: key.apiKey,
        api_secret: key.secretKey
    });
    
    const response = await client.getBalances().catch(error => {
        console.error(error);
    });

    const balances = Array.isArray(response) ? response.filter(coin => Number(coin.free) !== 0) : [];

    console.log(balances);
    
})();
