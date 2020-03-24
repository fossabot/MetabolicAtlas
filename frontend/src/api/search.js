import axios from 'axios';

const globalSearch = async (searchTerm) => {
  const { data } = await axios.get(`all/search/${searchTerm}`);
  return data;
};

export default { globalSearch };
