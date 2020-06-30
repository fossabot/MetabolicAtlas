import axios from 'axios';

const baseURL = '/api/v1/';

const fetchTissues = async (model) => {
  const { data } = await axios({ url: `${model}/gene/hpa_tissue/`, baseURL });
  return data;
};

const fetchRnaLevels = async (model, geneIds) => {
  const { data } = await axios({
    method: 'post',
    url: `${model}/gene/hpa_rna_levels/`,
    data: geneIds,
  });
  return data;
};

const fetchRnaLevelsForMap = async (model, mapType, dim, mapName) => {
  const { data } = await axios({ url: `${model}/gene/hpa_rna_levels/${mapType}/${dim}/${mapName}`, baseURL });
  return data;
};

export default { fetchTissues, fetchRnaLevels, fetchRnaLevelsForMap };
