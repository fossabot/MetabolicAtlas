import Vue from 'vue';
import Vuex from 'vuex';
import models from './modules/models';
import browserTiles from './modules/browserTiles';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    models,
    browserTiles,
  },
});
