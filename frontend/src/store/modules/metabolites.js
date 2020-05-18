import metabolitesApi from '@/api/metabolites';

const data = {
  metabolite: {},
  relatedMetabolites: [],
};

const actions = {
  async getMetaboliteData({ commit }, { model, id }) {
    const metabolite = await metabolitesApi.fetchMetaboliteData(model, id);
    commit('setMetabolite', metabolite);
  },
  async getRelatedMetabolites({ commit }, { model, id }) {
    const metabolites = await metabolitesApi.fetchRelatedMetabolites(model, id);
    commit('setRelatedMetabolites', metabolites);
  },
  clearRelatedMetabolites({ commit }) {
    commit('setRelatedMetabolites', []);
  },
};

const mutations = {
  setMetabolite: (state, metabolite) => {
    state.metabolite = metabolite;
  },
  setRelatedMetabolites: (state, metabolites) => {
    state.relatedMetabolites = metabolites;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
