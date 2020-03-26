import reactionsApi from '@/api/reactions';

const data = {
  relatedReactions: [],
};

const actions = {
  async getRelatedReactionsForGene({ commit }, { model, id }) {
    const reactions = await reactionsApi.fetchRelatedReactionsForGene(model, id);
    commit('setRelatedReactions', reactions);
  },
  async getRelatedReactionsForMetabolite({ commit }, { model, id, allCompartments }) {
    const reactions = await reactionsApi.fetchRelatedReactionsForMetabolite(model, id, allCompartments);
    commit('setRelatedReactions', reactions);
  },
  clearRelatedReactions({ commit }) {
    commit('setRelatedReactions', []);
  },
};

const mutations = {
  setRelatedReactions: (state, reactions) => {
    state.relatedReactions = reactions;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
