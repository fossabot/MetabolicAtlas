import browserTilesApi from '@/api/browserTiles';

const data = {
  tileComponents: null,
};

const actions = {
  async getBrowserTiles({ commit }) {
    const tileComponents = await browserTilesApi.fetchBrowserTiles({
      model: 'HumanGem',
      version: '1_3_0',
    });
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
