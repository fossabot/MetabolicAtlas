import browserTilesApi from '@/api/browserTiles';

const data = {
  tileComponents: null,
};

const actions = {
  async getBrowserTiles({ commit }, model) {
    const payload = {
      model: model.short_name.split('-').map(s => s[0] + s.slice(1).toLowerCase()).join(''),
      version: model.version.split('.').join('_'),
    };
    const tileComponents = await browserTilesApi.fetchBrowserTiles(payload);
    commit('setTileComponents', tileComponents);
  },
};

const mutations = {
  setTileComponents: (state, tileComponents) => {
    state.tileComponents = tileComponents;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
