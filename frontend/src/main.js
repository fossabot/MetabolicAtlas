import Vue from 'vue';
import VueMatomo from 'vue-matomo';
import axios from 'axios';
import vueDebounce from 'vue-debounce';
import NProgress from 'nprogress';
import App from './App';
import router from './router';
import { default as EventBus } from './event-bus';
import store from './store';
import { handleRouterClick, bindRouterLink } from './mixins/link-handler';

axios.defaults.baseURL = '/api';
axios.defaults.onDownloadProgress = function onDownloadProgress(progressEvent) {
  const percentCompleted = Math.floor((progressEvent.loaded * 100.0) / progressEvent.total);
  NProgress.set(percentCompleted / 100.0);
};

Vue.use(vueDebounce);

if (navigator.doNotTrack !== '1') {
  Vue.use(VueMatomo, {
    host: 'https://sysbiowiki.se:4433/',
    siteId: process.env.VUE_APP_MATOMOID,
    router,
  });
}

Vue.mixin({
  created() {
    bindRouterLink(this);
  },
  methods: {
    handleRouterClick,
  },
});

new Vue({ // eslint-disable-line no-new
  el: '#app',
  router,
  store,
  EventBus,
  render: h => h(App),
});
