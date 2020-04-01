import axios from 'axios';

const fetchCompartmentSummary = async (model, compartmentId) => {
  const { data } = await axios.get(`${model}/compartment/${compartmentId}/summary/`);
  return data;
};

export default { fetchCompartmentSummary };
