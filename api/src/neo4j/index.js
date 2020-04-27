import getCompartment from './queries/compartment.js';
import getGene from './queries/gene.js';
import getReaction from './queries/reaction.js';
import getSubsystem from './queries/subsystem.js';
import getMetabolite from './queries/metabolite.js';
import search from './queries/search.js';
import {
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
} from './queries/relatedReactions.js';

export {
  getCompartment,
  getGene,
  getReaction,
  getSubsystem,
  getMetabolite,
  search,
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
};
