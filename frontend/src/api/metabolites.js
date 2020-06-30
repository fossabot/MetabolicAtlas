import axios from 'axios';

const fetchMetaboliteData = async ({ id, version }) => {
  const { data } = await axios.get(`${version}/metabolites/${id}/`);
  return data;
};

const fetchRelatedMetabolites = async ({ id, version }) => {
  const { data } = await axios.get(`${version}/metabolites/${id}/related-metabolites`);
  return data.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
};

export default {
  fetchMetaboliteData,
  fetchRelatedMetabolites,
};
