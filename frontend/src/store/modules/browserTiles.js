import browserTilesApi from '@/api/browserTiles';

const data = {
  starredComponents: null,
};

const actions = {
  async getBrowserTiles({ commit, rootState }) {
    const model = rootState.models.model.database_name;
    const starredComponents = await browserTilesApi.fetchBrowserTiles(model);
    commit('setStarredComponents', starredComponents);
  },
};

const mutations = {
  setStarredComponents: (state, starredComponents) => {
    state.starredComponents = starredComponents;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
