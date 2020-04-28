import express from 'express';
import {
  getCompartment,
  getGene,
  getMetabolite,
  getReaction,
  getSubsystem,
  getRelatedReactionsForCompartment,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForReaction,
  getRelatedReactionsForSubsystem,
  search,
} from '../neo4j/index';

const neo4jRoutes = express.Router();

const fetchWith = async (req, res, getter) => {
  const { id, version } = req.params;
  try {
    const result = await getter({ id, version });
    res.json(result);
  } catch (e) {
    res.status(400).send(e);
  }
};

// 87yyt
neo4jRoutes.get('/:version/compartments/:id', async (req, res) => fetchWith(req, res, getCompartment));
neo4jRoutes.get('/:version/compartments/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForCompartment));

// w6ebb
neo4jRoutes.get('/:version/genes/:id', async (req, res) => fetchWith(req, res, getGene));
neo4jRoutes.get('/:version/genes/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForGene));

// uv580
neo4jRoutes.get('/:version/metabolites/:id', async (req, res) => fetchWith(req, res, getMetabolite));
neo4jRoutes.get('/:version/metabolites/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForMetabolite));

// meiup
neo4jRoutes.get('/:version/reactions/:id', async (req, res) => fetchWith(req, res, getReaction));
neo4jRoutes.get('/:version/reactions/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForReaction));

// 0uz10
neo4jRoutes.get('/:version/subsystems/:id', async (req, res) => fetchWith(req, res, getSubsystem));
neo4jRoutes.get('/:version/subsystems/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForSubsystem));

// /1/search?searchTerm=y50&model=Human
neo4jRoutes.get('/:version/search', async (req, res) => {
  const { version } = req.params;
  const { model, searchTerm } = req.query;

  try {
    const result = await search({ searchTerm, model, version });
    res.json(result);
  } catch (e) {
    res.status(400).send(e);
  }
});

export default neo4jRoutes;
