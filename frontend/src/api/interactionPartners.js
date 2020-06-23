import axios from 'axios';

const fetchInteractionPartners = async ({ id, version, model }) => {
  const { data } = await axios({ url: `${version}/interaction-partners/${id}?model=${model}`, baseURL: '/new_api/integrated' });
  return data;
};

export default { fetchInteractionPartners };
