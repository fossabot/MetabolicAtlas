import axios from 'axios';

const fetchTissues = async (model) => {
  const { data } = await axios.get(`${model}/gene/hpa_tissue/`);
  return data;
};

const fetchRnaLevels = async (model, geneIds) => {
  const { data } = await axios.post(`${model}/gene/hpa_rna_levels/`, { data: geneIds });
  return data;
};

export default { fetchTissues, fetchRnaLevels };
