import axios from 'axios';

const fetchAvailableMaps = async (model, mapType, id) => {
  const { data } = await axios.get(`${model}/available_maps/${mapType}/${id}`);
  return data;
};

const fetchMapsListing = async (model) => {
  const { data } = await axios.get(`${model}/viewer/`);
  return data;
};

export default { fetchAvailableMaps, fetchMapsListing };
