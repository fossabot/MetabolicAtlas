import metabolitesApi from '@/api/metabolites';

const data = {
  metabolite: {},
  relatedMetabolites: [],
};

const actions = {
  async getMetaboliteData({ commit }, { model, id }) {
    console.warn(`TODO: use model: ${model}`);

    const metabolite = await metabolitesApi.fetchMetaboliteData({ id, version: '1_3_0' });
    commit('setMetabolite', metabolite);
  },
  async getRelatedMetabolites({ commit }, { model, id }) {
    console.warn(`TODO: use model: ${model}`);

    const metabolites = await metabolitesApi.fetchRelatedMetabolites({ id, version: '1_3_0' });
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
