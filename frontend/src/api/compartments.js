import axios from 'axios';

const fetchCompartmentSummary = async ({ id, version }) => {
  const { data } = await axios.get(`${version}/compartments/${id}/`);
  return data;
};

export default { fetchCompartmentSummary };
