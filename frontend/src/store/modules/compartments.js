import compartmentsApi from '@/api/compartments';

const data = {
  compartmentSummary: {},
};

const getters = {
  info: state => state.compartmentSummary.info || {},
  subsystems: state => state.compartmentSummary.subsystems || [],
};

const actions = {
  async getCompartmentSummary({ commit }, { model, id }) {
    console.warn(`TODO: use model: ${model}`);

    const compartmentSummary = await compartmentsApi.fetchCompartmentSummary({ id, version: '1_3_0' });
    commit('setCompartmentSummary', compartmentSummary);

    commit('maps/setAvailableMaps', {
      '2d': {
        compartment: compartmentSummary.compartmentSVGs,
        subsystem: [],
      },
      '3d': { compartment: [{ id: compartmentSummary.info.id, customName: compartmentSummary.info.name }], subsystem: [] },
    }, { root: true });
  },
};

const mutations = {
  setCompartmentSummary: (state, compartmentSummary) => {
    state.compartmentSummary = compartmentSummary;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
