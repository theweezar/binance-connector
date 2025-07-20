'use strict';

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require('path');
const cwd = process.cwd();

module.exports = [
    {
        mode: 'development',
        entry: [
            path.join(cwd, 'web/js/chart.js'),
            path.join(cwd, 'web/js/bootstrap.js')
        ],
        output: {
            path: path.join(cwd, 'web/dist/resources'),
            filename: '[name].js'
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
                },
                {
                    test: /\.(scss)$/,
                    use: [
                        {
                            loader: MiniCssExtractPlugin.loader
                        },
                        {
                            loader: 'css-loader'
                        },
                        {
                            loader: 'postcss-loader',
                            options: {
                                postcssOptions: {
                                    plugins: function () {
                                        return [
                                            require('autoprefixer')
                                        ];
                                    }
                                }
                            }
                        },
                        {
                            loader: 'sass-loader',
                            options: {
                                sassOptions: {
                                    silenceDeprecations: [
                                        'import',
                                        'color-functions',
                                        'global-builtin',
                                        'mixed-decls',
                                        'legacy-js-api',
                                    ],
                                    quietDeps: true
                                }
                            }
                        }
                    ]
                }
            ]
        },
        target: ['web', 'es5'],
        plugins: [
            new MiniCssExtractPlugin({
                filename: '[name].css'
            })
        ]
    }
];
