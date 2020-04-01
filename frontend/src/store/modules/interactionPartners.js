/* eslint-disable no-unused-vars */

import interactionPartnersApi from '@/api/interactionPartners';
import { chemicalName } from '@/helpers/chemical-formatters';

const data = {
  interactionPartners: {},
  tooLargeNetworkGraph: false,
  expansion: {},
};

const getters = {
  component: state => state.interactionPartners.component || {},
  reactions: state => state.interactionPartners.reactions || [],
  title: (state, _getters) => (_getters.component.type === 'metabolite' ? chemicalName(_getters.component.name) : _getters.component.name),
  reactionsSet: (state, _getters) => new Set(_getters.reactions.map(r => r.id)),
  componentName: (state, _getters) => _getters.component.name || _getters.component.id,
};

const actions = {
  async getInteractionPartners({ commit }, { model, id }) {
    const interactionPartners = await interactionPartnersApi.fetchInteractionPartners(model, id);

    commit('setTooLargeNetworkGraph', !interactionPartners.reactions);
    commit('setInteractionPartners', interactionPartners);
  },

  async loadExpansion(args, { model, id }) {
    const { state, commit } = args;
    const _getters = args.getters; // eslint-disable-line no-underscore-dangle

    const expansion = await interactionPartnersApi.fetchInteractionPartners(model, id);

    commit('setTooLargeNetworkGraph', !expansion.reactions);
    commit('setExpansion', expansion);

    const newReactions = expansion.reactions.filter(r => !_getters.reactionsSet.has(r.id));
    const updatedInteractionPartners = {
      ...state.interactionPartners,
      reactions: [..._getters.reactions, ...newReactions],
    };

    commit('setInteractionPartners', updatedInteractionPartners);
  },
};

const mutations = {
  setInteractionPartners: (state, interactionPartners) => {
    state.interactionPartners = interactionPartners;
  },

  setTooLargeNetworkGraph: (state, tooLargeNetworkGraph) => {
    state.tooLargeNetworkGraph = tooLargeNetworkGraph;
  },

  setExpansion: (state, expansion) => {
    state.expansion = expansion;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
