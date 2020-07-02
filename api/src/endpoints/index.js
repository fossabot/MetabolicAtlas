import express from 'express';
import neo4jRoutes from './neo4j.js';
import repoRoutes from './repository.js';

const router = express.Router();

router.use(neo4jRoutes);
router.use('/repository', repoRoutes);

export default router;
