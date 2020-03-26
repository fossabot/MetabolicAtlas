import Vue from 'vue';
import Vuex from 'vuex';
import models from './modules/models';
import browserTiles from './modules/browserTiles';
import gems from './modules/gems';
import genes from './modules/genes';
import search from './modules/search';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    models,
    browserTiles,
    gems,
    genes,
    search,
  },
});
