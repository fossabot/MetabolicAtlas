import axios from 'axios';

const fetchReactionData = async ({ id, version }) => {
  const { data } = await axios.get(`${version}/reactions/${id}/`);
  return data;
};

const fetchRelatedReactionsForReaction = async ({ id, version, limit }) => {
  const { data } = await axios.get(`${version}/reactions/${id}/related-reactions?limit=${limit}`);
  return data.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
};

const fetchRelatedReactions = async (resourceType, id, version, limit) => {
  const { data } = await axios.get(`${version}/${resourceType}s/${id}/related-reactions?limit=${limit}`);
  return data;
};

const fetchRelatedReactionsForGene = async ({ id, version, limit }) => fetchRelatedReactions('gene', id, version, limit);

const fetchRelatedReactionsForMetabolite = async ({ id, version, limit }, allCompartments) => fetchRelatedReactions('metabolite', id, version, limit, allCompartments);

const fetchRelatedReactionsForSubsystem = async ({ id, version, limit }) => fetchRelatedReactions('subsystem', id, version, limit);

export default {
  fetchReactionData,
  fetchRelatedReactionsForReaction,
  fetchRelatedReactionsForGene,
  fetchRelatedReactionsForMetabolite,
  fetchRelatedReactionsForSubsystem,
};
