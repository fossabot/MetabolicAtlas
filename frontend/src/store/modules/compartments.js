import compartmentsApi from '@/api/compartments';

const data = {
  compartmentSummary: {},
};

const getters = {
  info: state => state.compartmentSummary || {},
  subsystems: state => state.compartmentSummary.subsystems || [],
};

const actions = {
  async getCompartmentSummary({ commit }, { model, id }) {
    console.warn(`TODO: use model: ${model}`);

    const compartmentSummary = await compartmentsApi.fetchCompartmentSummary({ id, version: '1' });
    commit('setCompartmentSummary', compartmentSummary);
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
