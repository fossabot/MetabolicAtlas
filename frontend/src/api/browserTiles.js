import axios from 'axios';

const fetchBrowserTiles = async ({ model, version }) => {
  const { data } = await axios.get(`${version}/random-components?model=${model}`);
  return data;
};

export default { fetchBrowserTiles };
