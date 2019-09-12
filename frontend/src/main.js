import axios from 'axios';
import Vue from 'vue';
import VueMatomo from 'vue-matomo';
import lodash from 'lodash';
import VueLodash from 'vue-lodash/dist/vue-lodash.min';
import App from './App';
import router from './router';
import { default as EventBus } from './event-bus';
import store from './store';

axios.defaults.baseURL = '/api';

Vue.use(VueLodash, lodash);

Vue.use(VueMatomo, {
  host: 'https://sysbiowiki.se:4433/',
  siteId: process.env.VUE_APP_MATOMOID,
  router,
});

new Vue({ // eslint-disable-line no-new
  el: '#app',
  router,
  store,
  EventBus,
  render: h => h(App),
});
