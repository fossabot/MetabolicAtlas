import { getGene } from '@/neo4j';

const data = {
  gene: {},
};

const getters = {
  geneName: state => state.gene.id,
};

const actions = {
  async getGeneData({ commit }, { model, id }) {
    console.warn(`TODO: use model: ${model}`);

    const gene = await getGene({ id, version: '1' });
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
