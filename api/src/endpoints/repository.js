import express from 'express';
import gemsRepoJson from './gemsRepository.json';
import integratedGemsRepoJson from './integratedModels.json';

const routes = express.Router();

routes.get('/integrated_models', async (req, res) => {
  try {
    res.json(integratedGemsRepoJson);
  } catch (e) {
    res.status(400).send(e);
  }
});

routes.get('/models', async (req, res) => {
  try {
    res.json(gemsRepoJson);
  } catch (e) {
    res.status(400).send(e);
  }
});

export default routes;
