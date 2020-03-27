import mapsApi from '@/api/maps';

const data = {
  availableMaps: {},
};

const actions = {
  async getAvailableMaps({ commit }, { model, mapType, id }) {
    const maps = await mapsApi.fetchAvailableMaps(model, mapType, id);
    commit('setAvailableMaps', maps);
  },
};

const mutations = {
  setAvailableMaps: (state, maps) => {
    state.availableMaps = maps;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
