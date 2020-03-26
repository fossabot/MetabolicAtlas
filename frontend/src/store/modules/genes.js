import genesApi from '@/api/genes';

const data = {
  gene: {},
};

const getters = {
  geneName: state => state.gene.geneName,
};

const actions = {
  async getGeneData({ commit }, { model, id }) {
    const gene = await genesApi.fetchGeneData(model, id);
    commit('setGene', gene);
  },
};

const mutations = {
  setGene: (state, gene) => {
    state.gene = gene;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
