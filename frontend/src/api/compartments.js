import axios from 'axios';

const fetchCompartmentSummary = async ({ id, version }) => {
  const { data } = await axios({ url: `${version}/compartments/${id}/`, baseURL: '/new_api/integrated' });
  return data;
};

export default { fetchCompartmentSummary };
