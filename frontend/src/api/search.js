import axios from 'axios';

const search = async ({ version, searchTerm, model, limit }) => {
  let url = `${version}/search?searchTerm=${searchTerm}`;
  if (model) {
    url += `&model=${model}`;
  }
  if (limit) {
    url += `&limit=${limit}`;
  }
  const { data } = await axios.get(url);
  return data;
};

export default { search };
