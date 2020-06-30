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
    const subsystemSummary = await subsystemsApi.fetchSubsystemSummary({ id, model, version: '1_3_0' });
    commit('setSubsystemSummary', subsystemSummary);

    commit('maps/setAvailableMaps', {
      '2d': {
        compartment: [],
        subsystem: subsystemSummary.subsystemSVGs,
      },
      '3d': { compartment: [], subsystem: [{ id: subsystemSummary.id, customName: subsystemSummary.name }] },
    }, { root: true });
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
