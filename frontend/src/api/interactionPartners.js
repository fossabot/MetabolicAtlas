import axios from 'axios';

const fetchInteractionPartners = async (model, id) => {
  const { data } = await axios.get(`${model}/reaction_components/${id}/with_interaction_partners`);
  return data;
};

export default { fetchInteractionPartners };
