import axios from 'axios';

const fetchMetaboliteData = async (model, id) => {
  const { data } = await axios.get(`${model}/metabolite/${id}/`);
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
