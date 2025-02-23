'use strict';

/** Packages */
const binance = require('binance');
const credentials = require('./scripts/input/credentials');
const { parseTimeString } = require('./scripts/utils');

/** Check credentials */
const key = credentials.getBinanceCredentials();

function Order(rawOrder) {
    this.symbol = rawOrder.symbol;
    this.side = rawOrder.side;
    this.origQty = Number(rawOrder.origQty);
    this.executedQty = Number(rawOrder.executedQty);
    this.cummulativeQuoteQty = Number(rawOrder.cummulativeQuoteQty);
    this.price = (this.cummulativeQuoteQty / this.executedQty).toFixed(2);
    this.time = parseTimeString(rawOrder.time);
}

(async () => {
    const client = new binance.MainClient({
        api_key: key.apiKey,
        api_secret: key.secretKey
    });

    const params = {
        // endTime: 0,
        // isIsolated: StringBoolean,
        // limit: number,
        // orderId: number,
        // startTime: number,
        symbol: 'XRPUSDT',
    };

    const response = await client.getAllOrders(params).catch(error => {
        console.error(error);
    });

    const filledOrders = Array.isArray(response)
        ? response.filter(rawOrder => rawOrder.status === 'FILLED')
            .map(rawOrder => (new Order(rawOrder)))
        : [];

    console.log(`Order count: ${filledOrders.length}`);
    console.log(filledOrders);
})();
