import axios from 'axios';

const fetchGeneData = async ({ id, version }) => {
  const { data } = await axios({ url: `${version}/genes/${id}/`, baseURL: '/new_api/integrated' });
  return { ...data, geneName: data.name || data.id };
};

export default { fetchGeneData };
