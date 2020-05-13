import axios from 'axios';

const fetchMetaboliteData = async ({ id, version }) => {
  const { data } = await axios({ url: `${version}/metabolites/${id}/`, baseURL: '/new_api/integrated' });
  return data;
};

const fetchRelatedMetabolites = async ({ id, version }) => {
  const { data } = await axios({ url: `${version}/metabolites/${id}/related-metabolites`, baseURL: '/new_api/integrated' });
  return data.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
};

export default {
  fetchMetaboliteData,
  fetchRelatedMetabolites,
};
