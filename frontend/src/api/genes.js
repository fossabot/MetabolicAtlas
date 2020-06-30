import axios from 'axios';

const fetchGeneData = async ({ id, version }) => {
  const { data } = await axios.get(`${version}/genes/${id}/`);
  return { ...data, geneName: data.name || data.id };
};

export default { fetchGeneData };
