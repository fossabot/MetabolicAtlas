import axios from 'axios';

const baseURL = '/api/v2/';

const fetchRnaLevels = async () => {
  const { data } = await axios({ url: '/rna/all/', baseURL });
  return data;
};

export default { fetchRnaLevels };
