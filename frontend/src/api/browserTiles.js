import axios from 'axios';

const fetchBrowserTiles = async (model) => {
  const { data } = await axios.get(`${model}/gem_browser_tiles/`);
  return data;
};

export default { fetchBrowserTiles };
