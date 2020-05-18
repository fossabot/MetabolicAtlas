import axios from 'axios';

const fetchReactionData = async ({ id, version }) => {
  const { data } = await axios({ url: `${version}/reactions/${id}/`, baseURL: '/new_api/integrated' });
  return data;
};

const fetchRelatedReactionsForReaction = async ({ id, version }) => {
  const { data } = await axios({ url: `${version}/reactions/${id}/related-reactions`, baseURL: '/new_api/integrated' });
  return data.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
};

const fetchRelatedReactions = async (resourceType, id, version, allCompartments = false) => {
  console.warn(`handle allCompartments: ${allCompartments}`);

  const { data } = await axios({ url: `${version}/${resourceType}s/${id}/related-reactions`, baseURL: '/new_api/integrated' });
  return data;
};

const fetchRelatedReactionsForGene = async ({ id, version }) => fetchRelatedReactions('gene', id, version);

const fetchRelatedReactionsForMetabolite = async ({ id, version }, allCompartments) => fetchRelatedReactions('metabolite', id, version, allCompartments);

const fetchRelatedReactionsForSubsystem = async ({ id, version }) => fetchRelatedReactions('subsystem', id, version);

export default {
  fetchReactionData,
  fetchRelatedReactionsForReaction,
  fetchRelatedReactionsForGene,
  fetchRelatedReactionsForMetabolite,
  fetchRelatedReactionsForSubsystem,
};
