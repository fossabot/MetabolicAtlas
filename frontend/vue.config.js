// vue.config.js
module.exports = {
  productionSourceMap: false,
  lintOnSave: 'default',
  css: {
    loaderOptions: {
      sass: {
        // @/ is an alias to src/  so this assumes you have a file named `src/vars.scss`
        data: `@import "~@/style/vars.scss";`
      },
    }
  },
  pluginOptions: {
    webpackBundleAnalyzer: {
      analyzerMode: process.env.NODE_ENV === 'development' ? 'server' : 'disabled',
      // Using the same host name as the container name
      analyzerHost: 'frontend',
      analyzerPort: 81,
      openAnalyzer: false
    }
  }
}
