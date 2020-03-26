import reactionsApi from '@/api/reactions';

const data = {
  relatedReactions: [],
  relatedReactionsLimit: 0,
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

  async getRelatedReactionsForSubsystem({ commit }, { model, id }) {
    const { reactions, limit } = await reactionsApi.fetchRelatedReactionsForSubsystem(model, id);
    commit('setRelatedReactions', reactions);
    commit('setRelatedReactionsLimit', limit);
  },

  clearRelatedReactions({ commit }) {
    commit('setRelatedReactions', []);
  },
};

const mutations = {
  setRelatedReactions: (state, reactions) => {
    state.relatedReactions = reactions;
  },
  setRelatedReactionsLimit: (state, limit) => {
    state.relatedReactionsLimit = limit;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
