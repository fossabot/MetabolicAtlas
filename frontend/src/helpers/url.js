const roundValue = value => Math.round((value + 0.00001) * 1000) / 1000;

const setRouteForMap = ({ route, mapType, mapId, dim }) => ({
  name: 'viewer',
  params: { ...route.params, type: mapType, map_id: mapId },
  query: { ...route.query, dim },
});

const setRouteForSel = ({ route, id }) => ({
  query: { ...route.query, sel: id },
});

const setRouteForSearch = ({ route, searchTerm }) => ({
  query: { ...route.query, search: searchTerm },
});

const setRouteForGeneExp1 = ({ route, tissue }) => ({
  query: { ...route.query, g1: tissue },
});

const setRouteForGeneExp2 = ({ route, tissue }) => ({
  query: { ...route.query, g2: tissue },
});

const setRouteForCoord = ({ route, x, y, z, u, v, w }) => {
  let coord = [x, y, z, u, v, w].map(val => roundValue(val)).join(',');
  const regex = /(?:-)?\d+(?:[.]\d+)?(?:[,](?:-)?\d+(?:[.]\d+)?){5}/g;
  coord = coord.match(regex) ? coord : '0,0,0,0,0,0';
  return {
    query: { ...route.query, coord },
  };
};

const setRouteForOverlay = ({ route, isOpen }) => ({
  query: { ...route.query, panel: isOpen ? '1' : '0' },
});

export {
  setRouteForMap,
  setRouteForSel,
  setRouteForSearch,
  setRouteForGeneExp1,
  setRouteForGeneExp2,
  setRouteForCoord,
  setRouteForOverlay,
};
