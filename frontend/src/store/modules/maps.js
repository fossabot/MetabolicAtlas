import mapsApi from '@/api/maps';

const data = {
  availableMaps: {},
  mapsListing: {
    compartment: [],
    subsystem: [],
    compartmentsvg: [],
    subsystemsvg: [],
  },
};

const getters = {
  mapsData3D: state => ({
    compartments: state.mapsListing.compartment.reduce((obj, c) => ({
      ...obj, [c.id]: { ...c, alternateDim: c.compartment_svg },
    }), {}),
    subsystems: state.mapsListing.subsystem.reduce((obj, s) => ({
      ...obj, [s.id]: { ...s, alternateDim: s.subsystem_svg },
    }), {}),
  }),

  compartmentMapping: state => ({
    dim3D: state.mapsListing.compartment.reduce((obj, c) => ({
      ...obj, [c.id]: c.compartment_svg,
    }), {}),
    dim2D: state.mapsListing.compartmentsvg.reduce((obj, c) => ({
      ...obj, [c.id]: c.compartment,
    }), {}),
  }),

  mapsData2D: state => ({
    compartments: state.mapsListing.compartmentsvg.reduce((obj, c) => ({
      ...obj, [c.id]: { ...c, alternateDim: c.compartment },
    }), {}),
    subsystems: state.mapsListing.subsystemsvg.reduce((obj, s) => ({
      ...obj, [s.id]: { ...s, alternateDim: s.subsystem },
    }), {}),
  }),

  has2DCompartmentMaps: (state, _getters) => Object.keys(_getters.mapsData2D.compartments).length > 0, // eslint-disable-line no-unused-vars

  has2DSubysystemMaps: (state, _getters) => Object.keys(_getters.mapsData2D.subsystems).length > 0, // eslint-disable-line no-unused-vars
};

const actions = {
  async getAvailableMaps({ commit }, { model, mapType, id }) {
    const maps = await mapsApi.fetchAvailableMaps(model, mapType, id);
    commit('setAvailableMaps', maps);
  },

  async getMapsListing({ commit }, model) {
    const mapsListing = await mapsApi.fetchMapsListing(model);
    commit('setMapsListing', mapsListing);
  },
};

const mutations = {
  setAvailableMaps: (state, maps) => {
    state.availableMaps = maps;
  },

  setMapsListing: (state, mapsListing) => {
    state.mapsListing = mapsListing;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
