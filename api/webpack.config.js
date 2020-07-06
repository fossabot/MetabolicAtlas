const path = require("path");
const nodeExternals = require("webpack-node-externals");
const NodemonPlugin = require('nodemon-webpack-plugin');

module.exports = {
  mode: process.env.NODE_ENV === "develop" ? "development" : "production",

  entry: path.resolve(__dirname, "src/index.js"),

  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "bundle.js",
  },

  target: 'node',

  externals: [nodeExternals()],

  plugins: [new NodemonPlugin()],

  watchOptions: {
    poll: 1000, // Check for changes every second
    ignored: /node_modules/,
  },

  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: ['@babel/preset-env'],
            },
          },
        ],
      },
    ],
  },
};
