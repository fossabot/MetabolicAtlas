import axios from 'axios';

const fetchModels = async () => {
  const { data } = await axios({ url: 'integrated_models/', baseURL: '/new_api/repository/' });
  return data;
};

export default { fetchModels };
