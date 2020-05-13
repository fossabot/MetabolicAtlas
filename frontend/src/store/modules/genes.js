import genesApi from '@/api/genes';

const data = {
  gene: {},
};

const getters = {
  geneName: state => state.gene.id,
};

const actions = {
  async getGeneData({ commit }, { model, id }) {
    console.warn(`TODO: use model: ${model}`);

    const gene = await genesApi.fetchGeneData({ id, version: '1_3_0' });
    commit('setGene', gene);
    commit('maps/setAvailableMaps', {
      '2d': {
        compartment: gene.compartmentSVGs,
        subsystem: gene.subsystemSVGs,
      },
      '3d': { compartment: [], subsystem: [] },
    }, { root: true });
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
