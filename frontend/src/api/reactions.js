import axios from 'axios';

const fetchRelatedReactions = async (model, resourceType, id, allCompartments = false) => {
  let url = `${model}/${resourceType}/${id}/get_reactions/`;
  if (allCompartments) {
    url += 'all_compartments/';
  }
  const { data } = await axios.get(url);
  return data;
};

const fetchRelatedReactionsForGene = async (model, id) => fetchRelatedReactions(model, 'gene', id);

const fetchRelatedReactionsForMetabolite = async (model, id, allCompartments) => fetchRelatedReactions(model, 'metabolite', id, allCompartments);

const fetchRelatedReactionsForSubsystem = async (model, id) => fetchRelatedReactions(model, 'subsystem', id);

export default {
  fetchRelatedReactionsForGene,
  fetchRelatedReactionsForMetabolite,
  fetchRelatedReactionsForSubsystem,
};
