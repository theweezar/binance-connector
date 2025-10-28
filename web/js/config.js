'use strict';

(function () {
    /**
     * Format a number to a fixed decimal string.
     * @param {number} value - The number to format.
     * @param {number} fixed - The number of decimal places.
     * @returns {string} - Formatted number as a string.
     */
    function parseFixed(value, fixed) {
        var num = Number(value);
        return !isNaN(num) ? num.toFixed(fixed) : '';
    }

    window.config = {
        LineSeries: {
            // ma_20: {
            //     color: '#39e75f'
            // },
            // ma_50: {
            //     color: '#f7b731'
            // },
            // ma_9: {
            //     color: '#39e75f'
            // },
            // ma_21: {
            //     color: '#f7b731'
            // },
            ema_fast: {
                color: '#39e75f'
            },
            ema_slow: {
                color: '#f7b731'
            },
            // ema_50: {
            //     color: '#f7b731'
            // }
            // support: {
            //     color: '#00FF00',
            // },
            // resistance: {
            //     color: '#FF0000',
            // }
        },
        Tooltip: [
            {
                label: 'High',
                value: 'high',
                style: 'margin-bottom: 2px; color: black;'
            },
            {
                label: 'Low',
                value: 'low',
                style: 'margin-bottom: 2px; color: black;'
            },
            {
                label: 'RSI (9)',
                value: 'rsi_9',
                parseValue: (value) => parseFixed(value, 2),
                style: 'margin-bottom: 2px; color: black;'
            },
            // {
            //     label: 'RSI high (9)',
            //     value: 'rsi_9_high',
            //     parseValue: (value) => parseFixed(value, 2),
            //     style: 'margin-bottom: 2px; color: red;'
            // },
            // {
            //     label: 'RSI low (9)',
            //     value: 'rsi_9_low',
            //     parseValue: (value) => parseFixed(value, 2),
            //     style: 'margin-bottom: 2px; color: green;'
            // }
        ]
    };
})();
