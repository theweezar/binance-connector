'use strict';

const { Bot } = require('grammy');
const path = require('path');
const cwd = process.cwd();
const exportDirPath = path.join(cwd, 'ignore');
const api = require(path.join(exportDirPath, 'api', 'fetch.json'));
const credentials = require('./scripts/input/credentials');

/** Check credentials */
const key = credentials.getTelegramCredentials();
if (!key || !key.apiKey || !key.chatID) {
    throw new Error('Telegram key not found');
}

const bot = new Bot(key.apiKey);
const components = [];
const processor = api.processor;
const text = `
<b>SYMBOL</b>: ${api.symbol}
<b>TIME (GMT+00)</b>: ${processor.openTime}  ➡️  ${processor.closeTime}
<b>OPEN</b>: ${processor.open}
<b>CLOSE</b>: ${processor.close}
<b>HIGH</b>: ${processor.high}
<b>LOW</b>: ${processor.low}
<b>TYPE</b>: ${processor.type === 'U' ? 'UP' : 'DOWN'}
<b>RSI 7</b>: ${processor.rsi7}
<b>RSI 14</b>: ${processor.rsi14}
<b>RSI 30</b>: ${processor.rsi30}
`;

components.push(text);

if (api.signal && api.signal.ema34XEma89 && Object.keys(api.signal.ema34XEma89).length) {
    const emaSignal = api.signal.ema34XEma89;
    const signalText = `---
EMA34 ⚔️ EMA89: <b><u>${emaSignal.direction.toUpperCase()}</u></b>
<i>at</i> ${emaSignal.openTime}  ➡️  ${emaSignal.closeTime}
    `;
    components.push(signalText);
}

// https://core.telegram.org/bots/api#sendmessage
bot.api.sendMessage(key.chatID, components.join(''), {
    parse_mode: 'HTML'
});
