import reactionsApi from '@/api/reactions';

const data = {
  reaction: {},
  referenceList: [],
  relatedReactions: [],
  relatedReactionsLimit: 200,
};

const constructCompartmentStr = (reaction) => {
  const compartments = reaction.compartments.reduce((obj, { id, ...cs }) => ({
    ...obj,
    [id]: cs,
  }), {});

  const reactants = reaction.metabolites.filter(m => m.outgoing);
  const products = reaction.metabolites.filter(m => !m.outgoing);
  const reactantsCompartments = Array.from(new Set(
    reactants.map(r => compartments[r.compartmentId].name)
  )).join(' + ');
  const productsCompartments = Array.from(new Set(
    products.map(r => compartments[r.compartmentId].name)
  )).join(' + ');

  return `${reactantsCompartments} => ${productsCompartments}`;
};

const actions = {
  async getReactionData({ commit }, { model, id }) {
    console.warn(`TODO: use real model: ${model} and id: ${id}`);

    const { pubmedIds, ...reaction } = await reactionsApi.fetchReactionData({ id, version: '1_3_0' });

    commit('setReaction', {
      ...reaction,
      compartment_str: reaction.compartments.map(c => c.name).join(', '),
      reactionreactant_set: reaction.metabolites.filter(m => m.outgoing),
      reactionproduct_set: reaction.metabolites.filter(m => !m.outgoing),
    });

    commit('maps/setAvailableMaps', {
      '2d': {
        compartment: reaction.compartmentSVGs,
        subsystem: reaction.subsystemSVGs,
      },
      '3d': { compartment: [], subsystem: [] },
    }, { root: true });

    const pmids = pubmedIds.map(pm => pm.id);
    commit('setReferenceList', pmids);
  },
  async getRelatedReactionsForReaction({ commit, state }, { model, id }) {
    console.warn(`TODO: use real model: ${model} and id: ${id}`);

    const reactions = await reactionsApi.fetchRelatedReactionsForReaction({ id, version: '1_3_0', limit: state.relatedReactionsLimit });
    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: constructCompartmentStr(r),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
  },
  async getRelatedReactionsForGene({ commit, state }, { model, id }) {
    console.warn(`TODO: use real model: ${model} and id: ${id}`);

    const reactions = await reactionsApi.fetchRelatedReactionsForGene({ id, version: '1_3_0', limit: state.relatedReactionsLimit });
    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: constructCompartmentStr(r),
        subsystem_str: r.subsystems.map(s => s.name).join(', '),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
    // commit('setRelatedReactionsLimit', limit);
  },
  async getRelatedReactionsForMetabolite({ commit, state }, { model, id }) {
    console.warn(`TODO: use real model: ${model} and id: ${id}`);

    const reactions = await reactionsApi.fetchRelatedReactionsForMetabolite({ id, version: '1_3_0', limit: state.relatedReactionsLimit });

    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: constructCompartmentStr(r),
        subsystem_str: r.subsystems.map(s => s.name).join(', '),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
    // commit('setRelatedReactionsLimit', limit);
  },
  async getRelatedReactionsForSubsystem({ commit, state }, { model, id }) {
    console.warn(`TODO: use real model: ${model}`);

    const reactions = await reactionsApi.fetchRelatedReactionsForSubsystem({ id, version: '1_3_0', limit: state.relatedReactionsLimit });

    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: constructCompartmentStr(r),
        subsystem_str: r.subsystems.map(s => s.name).join(', '),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
    // commit('setRelatedReactionsLimit', limit);
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
