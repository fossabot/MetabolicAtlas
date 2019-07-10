// vue.config.js
module.exports = {
  productionSourceMap: false,
  pluginOptions: {
    webpackBundleAnalyzer: {
      analyzerMode: process.env.NODE_ENV === 'development' ? 'server' : 'disabled',
      analyzerHost: 'frontend',
      analyzerPort: 81,
      openAnalyzer: false
    }
  }
}
