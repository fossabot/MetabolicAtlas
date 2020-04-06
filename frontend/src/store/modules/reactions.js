import reactionsApi from '@/api/reactions';

const data = {
  reaction: {},
  referenceList: [],
  relatedReactions: [],
  relatedReactionsLimit: 0,
};

const actions = {
  async getReactionData({ commit }, { model, id }) {
    const { reaction, pmids } = await reactionsApi.fetchReactionData(model, id);
    commit('setReaction', reaction);
    if (pmids.length !== 0) {
      commit('setReferenceList', pmids);
    }
  },
  async getRelatedReactionsForReaction({ commit }, { model, id }) {
    const reactions = await reactionsApi.fetchRelatedReactionsForReaction(model, id);
    commit('setRelatedReactions', reactions);
  },
  async getRelatedReactionsForGene({ commit }, { model, id }) {
    const { reactions, limit } = await reactionsApi.fetchRelatedReactionsForGene(model, id);
    commit('setRelatedReactions', reactions);
    commit('setRelatedReactionsLimit', limit);
  },
  async getRelatedReactionsForMetabolite({ commit }, { model, id, allCompartments }) {
    const { reactions, limit } = await reactionsApi.fetchRelatedReactionsForMetabolite(model, id, allCompartments);
    commit('setRelatedReactions', reactions);
    commit('setRelatedReactionsLimit', limit);
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
  setReaction: (state, reaction) => {
    state.reaction = reaction;
  },
  setReferenceList: (state, referenceList) => {
    state.referenceList = referenceList;
  },
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
