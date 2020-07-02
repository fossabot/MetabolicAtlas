import express from 'express';
import hpaJson from '../data/hpaRna.json';

const routes = express.Router();

routes.get('/all', async (req, res) => {
  try {
    res.json(hpaJson);
  } catch (e) {
    res.status(400).send(e);
  }
});

export default routes;
