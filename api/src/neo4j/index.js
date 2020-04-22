import getReaction from './queries/reaction.js';
import getGene from './queries/gene.js';
import getMetabolite from './queries/metabolite.js';
import {
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
} from './queries/relatedReactions.js';

export {
  getReaction,
  getGene,
  getMetabolite,
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
};
