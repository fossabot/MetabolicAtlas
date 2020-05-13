const path = require('path');

module.exports = {
  entry: {
    main: './src/index.js',
  },

  output: {
    path: path.join(__dirname, 'out'),
    filename: 'bundle.js',
  },

  target: 'node',
  mode: 'development',

  watchOptions: {
    poll: 1000, // Check for changes every second
  },
};
