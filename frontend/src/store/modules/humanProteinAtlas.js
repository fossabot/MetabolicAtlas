import hpaApi from '@/api/humanProteinAtlas';

const data = {
  tissues: {},
  matLevels: [],
  mapRnaLevels: null,
};

const getters = {
  HPATissues: state => state.tissues.HPA,
};

const actions = {
  async getTissues({ commit }, model) {
    const tissues = await hpaApi.fetchTissues(model);
    commit('setTissues', { HPA: tissues });
  },
  async getMatLevels({ commit }, { model, geneIds }) {
    const { levels } = await hpaApi.fetchRnaLevels(model, geneIds);
    commit('setMatLevels', levels);
  },
  async getRnaLevelsForMap({ commit }, { model, mapType, dim, mapName }) {
    const levels = await hpaApi.fetchRnaLevelsForMap(model, mapType, dim, mapName);
    commit('setMapRnaLevels', levels);
  },
};

const mutations = {
  setTissues: (state, tissues) => {
    state.tissues = tissues;
  },
  setMatLevels: (state, matLevels) => {
    state.matLevels = matLevels;
  },
  setMapRnaLevels: (state, mapRnaLevels) => {
    state.mapRnaLevels = mapRnaLevels;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
