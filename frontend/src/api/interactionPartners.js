import axios from 'axios';

const fetchInteractionPartners = async ({ id, version, model }) => {
  const { data } = await axios.get(`${version}/interaction-partners/${id}?model=${model}`);
  return data;
};

export default { fetchInteractionPartners };
