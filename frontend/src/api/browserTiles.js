import axios from 'axios';

const fetchBrowserTiles = async ({ model, version }) => {
  const { data } = await axios({ url: `${version}/random-components?model=${model}`, baseURL: '/new_api/integrated' });
  return data;
};

export default { fetchBrowserTiles };
