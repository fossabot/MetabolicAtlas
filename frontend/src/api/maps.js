import axios from 'axios';

const fetchAvailableMaps = async (model, mapType, id) => {
  const { data } = await axios.get(`${model}/available_maps/${mapType}/${id}`);
  return data;
};

const fetchMapsListing = async (model) => {
  const { data } = await axios.get(`${model}/viewer/`);
  return data;
};

const fetchSvgMap = async (mapUrl, model, svgName) => {
  const { data } = await axios.get(`${mapUrl}/${model}/${svgName}`);
  return data;
};

const mapSearch = async (model, searchTerm) => {
  const { data } = await axios.get(`${model}/get_id/${searchTerm}`);
  return data;
};

export default { fetchAvailableMaps, fetchMapsListing, fetchSvgMap, mapSearch };
