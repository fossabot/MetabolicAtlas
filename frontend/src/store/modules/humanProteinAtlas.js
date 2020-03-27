import hpaApi from '@/api/humanProteinAtlas';

const data = {
  tissues: {},
  matLevels: [],
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
};

const mutations = {
  setTissues: (state, tissues) => {
    state.tissues = tissues;
  },

  setMatLevels: (state, matLevels) => {
    state.matLevels = matLevels;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
