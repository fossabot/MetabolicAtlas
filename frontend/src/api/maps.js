import axios from 'axios';

const fetchAvailableMaps = async (model, mapType, id) => {
  const { data } = await axios.get(`${model}/available_maps/${mapType}/${id}`);
  return data;
};

export default { fetchAvailableMaps };
