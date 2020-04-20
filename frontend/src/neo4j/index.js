import getReaction from './queries/reaction';
import getGene from './queries/gene';
import getMetabolite from './queries/metabolite';
import {
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
} from './queries/relatedReactions';

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
