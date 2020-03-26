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
    const compartmentSummary = await compartmentsApi.fetchCompartmentSummary(model, id);
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
