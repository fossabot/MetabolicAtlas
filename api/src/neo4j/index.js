import getCompartment from './queries/compartment.js';
import getGene from './queries/gene.js';
import getReaction from './queries/reaction.js';
import getSubsystem from './queries/subsystem.js';
import getMetabolite from './queries/metabolite.js';
import { modelSearch, globalSearch } from './queries/search.js';
import {
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
} from './queries/relatedReactions.js';
import getRelatedMetabolites from './queries/relatedMetabolites.js';
import getRandomComponents from './queries/randomComponents.js';
import getInteractionPartners from './queries/interactionPartners.js';

export {
  getCompartment,
  getGene,
  getReaction,
  getSubsystem,
  getMetabolite,
  modelSearch,
  globalSearch,
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
  getRelatedMetabolites,
  getRandomComponents,
  getInteractionPartners,
};
