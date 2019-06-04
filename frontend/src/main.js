// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import axios from 'axios';
import Vue from 'vue';
import VueMatomo from 'vue-matomo';
import lodash from 'lodash';
import VueLodash from 'vue-lodash/dist/vue-lodash.min';
import App from './App';
import router from './router';
import { EventBus } from './event-bus';

axios.defaults.baseURL = '/api';

Vue.use(VueLodash, lodash);

Vue.use(VueMatomo, {
  host: 'https://sysbiowiki.se:4433/',
  siteId: 14,
  router,
});

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  EventBus,
  template: '<App/>',
  components: { App },
});
