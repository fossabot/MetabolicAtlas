import subsystemsApi from '@/api/subsystems';

const data = {
  subsystemSummary: {},
};

const getters = {
  info: state => state.subsystemSummary || {},
  metabolites: state => state.subsystemSummary.metabolites || [],
  genes: state => state.subsystemSummary.genes || [],
  limitMetabolite: state => state.subsystemSummary.limit || 1000,
  limitGene: state => state.subsystemSummary.limit || 1000,
};

const actions = {
  async getSubsystemSummary({ commit }, { model, id }) {
    console.warn(`TODO: use model: ${model}`);

    const subsystemSummary = await subsystemsApi.fetchSubsystemSummary({ id, version: '1' });
    commit('setSubsystemSummary', subsystemSummary);
  },
};

const mutations = {
  setSubsystemSummary: (state, subsystemSummary) => {
    state.subsystemSummary = subsystemSummary;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
