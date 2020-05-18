import axios from 'axios';

const fetchMetaboliteData = async ({ id, version }) => {
  const { data } = await axios({ url: `${version}/metabolites/${id}/`, baseURL: '/new_api/integrated' });
  return data;
};

const fetchRelatedMetabolites = async (model, id) => {
  const { data } = await axios.get(`${model}/metabolite/${id}/related`);
  return data.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
};

export default {
  fetchMetaboliteData,
  fetchRelatedMetabolites,
};
