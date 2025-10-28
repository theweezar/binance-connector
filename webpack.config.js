'use strict';

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require('path');
const fs = require('fs');
const cwd = process.cwd();

/**
 * Lists all .js files in the client/js folder.
 * @returns {Object} An object where keys are filenames without extensions and values are full paths.
 */
const listJSFiles = () => {
  const folderPath = path.join(cwd, 'web/js');
  try {
    const files = fs.readdirSync(folderPath, { withFileTypes: true });
    const result = {};
    files
      .filter(file => file.isFile() && file.name.endsWith('.js'))
      .forEach(file => {
        const name = path.basename(file.name, path.extname(file.name));
        result[name] = path.join(folderPath, file.name);
      });
    return result;
  } catch (error) {
    console.error(`Error reading folder: ${error.message}`);
    throw error;
  }
};

module.exports = [
  {
    mode: 'development',
    entry: listJSFiles(),
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
