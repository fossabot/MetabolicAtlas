import reactionsApi from '@/api/reactions';
import {
  getReaction,
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
} from '@/neo4j';

const data = {
  reaction: {},
  referenceList: [],
  relatedReactions: [],
  relatedReactionsLimit: 0,
};

const actions = {
  async getReactionData({ commit }, { model, id }) {
    console.warn(`TODO: use real model: ${model} and id: ${id}`);

    const { pubmedIds, ...reaction } = await getReaction({ id: 'meiup', version: '1' });

    commit('setReaction', {
      ...reaction,
      compartment_str: reaction.compartments.map(c => c.name).join(', '),
      reactionreactant_set: reaction.metabolites.filter(m => m.outgoing),
      reactionproduct_set: reaction.metabolites.filter(m => !m.outgoing),
    });

    const pmids = pubmedIds.map(pm => pm.pubmedId);
    if (pmids.length !== 0) {
      commit('setReferenceList', pmids);
    }
  },
  async getRelatedReactionsForReaction({ commit }, { model, id }) {
    console.warn(`TODO: use real model: ${model} and id: ${id}`);

    const reactions = await getRelatedReactionsForReaction({ id: 'meiup', version: '1' });
    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: r.compartments.map(c => c.name).join(', '),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
  },
  async getRelatedReactionsForGene({ commit }, { model, id }) {
    console.warn(`TODO: use real model: ${model} and id: ${id}`);

    const reactions = await getRelatedReactionsForGene({ id, version: '1' });
    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: r.compartments.map(c => c.name).join(', '),
        subsystem_str: r.subsystems.map(s => s.name).join(', '),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
    // commit('setRelatedReactionsLimit', limit);
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
