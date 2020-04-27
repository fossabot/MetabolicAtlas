import browserTilesApi from '@/api/browserTiles';

const data = {
  tileComponents: null,
};

const actions = {
  async getBrowserTiles({ commit, rootState }) {
    const model = rootState.models.model.database_name;
    const tileComponents = await browserTilesApi.fetchBrowserTiles(model);
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
