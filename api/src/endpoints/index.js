import express from 'express';
import neo4jRoutes from './neo4j';
import repoRoutes from './repository';
import hpaRoutes from './hpaRna';

const router = express.Router();

router.use(neo4jRoutes);
router.use('/repository', repoRoutes);
router.use('/rna', hpaRoutes);

export default router;
