import searchApi from '@/api/search';

const data = {
  categories: [
    'metabolite',
    'gene',
    'reaction',
    'subsystem',
    'compartment',
  ],
  globalResults: {},
};

const getters = {
  categorizedResults: (state) => {
    const results = {
      metabolite: [],
      gene: [],
      reaction: [],
      subsystem: [],
      compartment: [],
    };

    Object.keys(state.globalResults).forEach((model) => {
      const resultsModel = state.globalResults[model];
      state.categories.filter(resultType => resultsModel[resultType])
        .forEach((resultType) => {
          results[resultType] = results[resultType].concat(
            resultsModel[resultType].map(
              (e) => {
                const d = e; d.model = { id: model, name: resultsModel.name }; return d;
              })
          );
        });
    });

    return results;
  },
  categorizedResultsCount: (state, _getters) => Object.fromEntries( // eslint-disable-line no-unused-vars
    Object.entries(_getters.categorizedResults).map(([k, v]) => [k, v.length])),
};

const actions = {
  async globalSearch({ commit }, searchTerm) {
    const results = await searchApi.globalSearch(searchTerm);
    commit('setGlobalResults', results);
  },
  clearGlobalSearchResults({ commit }) {
    commit('setGlobalResults', {});
  },
};

const mutations = {
  setGlobalResults: (state, globalResults) => {
    state.globalResults = globalResults;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
