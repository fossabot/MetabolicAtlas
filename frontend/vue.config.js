// vue.config.js

const IS_DEV = process.env.NODE_ENV === 'development';

module.exports = {
  productionSourceMap: false,
  lintOnSave: IS_DEV,
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
      analyzerMode: IS_DEV ? 'server' : 'disabled',
      // Using the same host name as the container name
      analyzerHost: 'frontend',
      analyzerPort: 81,
      openAnalyzer: false
    }
  }
}
