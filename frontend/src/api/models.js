import axios from 'axios';

const fetchModels = async () => {
  const { data } = await axios.get('models/');
  return data;
};

export default { fetchModels };
