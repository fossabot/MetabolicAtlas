import axios from 'axios';

const fetchRelatedReactions = async (model, resourceType, id) => {
  const { data } = await axios.get(`${model}/${resourceType}/${id}/get_reactions`);
  return data;
};

const fetchRelatedReactionsForGene = async (model, id) => fetchRelatedReactions(model, 'gene', id);

export default { fetchRelatedReactionsForGene };
