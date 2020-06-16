import axios from 'axios';

const globalSearch = async (searchTerm) => {
  const { data } = await axios.get(`all/search/${searchTerm}`);
  return data;
};

const search = async ({ version, searchTerm, model, limit }) => {
  let url = `${version}/search?searchTerm=${searchTerm}`;
  if (model) {
    url += `&model=${model}`;
  }
  if (limit) {
    url += `&limit=${limit}`;
  }
  const { data } = await axios({ url, baseURL: '/new_api/integrated' });
  return data;
};

export default { globalSearch, search };
