'use strict';

const path = require('path');
const cwd = process.cwd();

module.exports = [
    {
        mode: 'development',
        entry: path.join(cwd, 'web/js/chart.js'),
        output: {
            path: path.join(cwd, 'web/dist/js'),
            filename: 'chart.js'
        },
        module: {
            rules: [
                {
                    test: /\.m?js$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            presets: ['@babel/preset-env'],
                            cacheDirectory: true
                        }
                    }
                }
            ]
        },
        target: ['web', 'es5']
    }
];
