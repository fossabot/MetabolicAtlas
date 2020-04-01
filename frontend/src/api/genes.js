import axios from 'axios';

const fetchGeneData = async (model, geneId) => {
  const { data } = await axios.get(`${model}/gene/${geneId}`);
  return { ...data, geneName: data.name || data.id };
};

export default { fetchGeneData };
