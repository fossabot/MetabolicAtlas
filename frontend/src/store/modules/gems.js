import gemsApi from '@/api/gems';

const data = {
  gem: null,
  gemList: [],
};

const getters = {
  setFilterOptions: state => [...new Set(state.gemList.map(g => g.set_name))].sort(),
  systemFilterOptions: state => [...new Set(state.gemList.map(g => g.organ_system))].sort(),
  conditionFilterOptions: state => [...new Set(state.gemList.map(g => g.condition))].sort(),
};

const actions = {
  async getGems({ commit }) {
    const gems = await gemsApi.fetchGems();
    commit('setGemList', gems);
  },
  async getGemData({ commit }, id) {
    const gem = await gemsApi.fetchGemData(id);
    commit('setGem', gem);
  },
};

const mutations = {
  setGem: (state, gem) => {
    state.gem = gem;
  },
  setGemList: (state, gemList) => {
    state.gemList = gemList;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
