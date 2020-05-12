import axios from 'axios';

const globalSearch = async (searchTerm) => {
  const { data } = await axios.get(`all/search/${searchTerm}`);
  return data;
};

const search = async (model, metabolitesAndGenesOnly, searchTerm) => {
  const url = `${model}/search_${metabolitesAndGenesOnly ? 'ip' : 'gb'}/${searchTerm}`;
  const { data } = await axios.get(url);
  return data;
};

export default { globalSearch, search };
