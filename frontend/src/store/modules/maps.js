import mapsApi from '@/api/maps';
import genesApi from '@/api/genes';
import reactionsApi from '@/api/reactions';
import metabolitesApi from '@/api/metabolites';

const data = {
  availableMaps: {},
  mapsListing: {
    compartment: [],
    subsystem: [],
    compartmentsvg: [],
    subsystemsvg: [],
  },
  svgMap: null,
  idsFound: [],
  selectedElement: null,
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

  has2DSubsystemMaps: (state, _getters) => Object.keys(_getters.mapsData2D.subsystems).length > 0, // eslint-disable-line no-unused-vars
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

  async getSvgMap({ commit }, { mapUrl, model, svgName }) {
    const svgMap = await mapsApi.fetchSvgMap(mapUrl, model, svgName);
    commit('setSvgMap', svgMap);
  },

  setSvgMap({ commit }, svgMap) {
    commit('setSvgMap', svgMap);
  },

  async mapSearch({ commit }, { model, searchTerm }) {
    const idsFound = await mapsApi.mapSearch(model, searchTerm);
    commit('setIdsFound', idsFound);
  },

  setIdsFound({ commit }, idsFound) {
    commit('setIdsFound', idsFound);
  },

  async getSelectedElement({ commit }, { model, type, id }) {
    let apiFunc;

    console.log(type);
    switch (type) {
      case 'gene':
        apiFunc = genesApi.fetchGeneData;
        break;
      case 'reaction':
        apiFunc = reactionsApi.fetchReactionData;
        break;
      case 'metabolite':
        apiFunc = metabolitesApi.fetchMetaboliteData;
        break;
      default:
        // TODO: handle unexpected type
        break;
    }

    const selectedElement = await apiFunc(model, id);
    commit('setSelectedElement', selectedElement);
  },
};

const mutations = {
  setAvailableMaps: (state, maps) => {
    state.availableMaps = maps;
  },

  setMapsListing: (state, mapsListing) => {
    state.mapsListing = mapsListing;
  },

  setSvgMap: (state, svgMap) => {
    state.svgMap = svgMap;
  },

  setIdsFound: (state, idsFound) => {
    state.idsFound = idsFound;
  },

  setSelectedElement: (state, selectedElement) => {
    state.selectedElement = selectedElement;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
