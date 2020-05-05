import getCompartment from './queries/compartment';
import getGene from './queries/gene';
import getReaction from './queries/reaction';
import getSubsystem from './queries/subsystem';
import getMetabolite from './queries/metabolite';
import search from './queries/search';
import {
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
} from './queries/relatedReactions';
import getRelatedMetabolites from './queries/relatedMetabolites';

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
  getRelatedMetabolites,
};
