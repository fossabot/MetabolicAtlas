import modelsApi from '@/api/models';

const data = {
  model: null,
  models: {},
};

const getters = {
  model: state => state.model,
  models: state => state.models,
};

const actions = {
  async getModels({ commit }) {
    const models = await modelsApi.fetchModels();
    commit('setModels', models);
  },
  selectModel({ commit }, model) {
    commit('setModel', model);
  },
};

const mutations = {
  setModel: (state, model) => {
    state.model = model;
  },
  setModels: (state, models) => {
    state.models = models;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
