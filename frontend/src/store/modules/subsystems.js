import subsystemsApi from '@/api/subsystems';

const data = {
  subsystemSummary: {},
};

const getters = {
  info: state => state.subsystemSummary.info || {},
  metabolites: state => state.subsystemSummary.metabolites || [],
  genes: state => state.subsystemSummary.genes || [],
  limitMetabolite: state => state.subsystemSummary.limit || 0,
  limitGene: state => state.subsystemSummary.limit || 0,
};

const actions = {
  async getSubsystemSummary({ commit }, { model, id }) {
    const subsystemSummary = await subsystemsApi.fetchSubsystemSummary(model, id);
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
