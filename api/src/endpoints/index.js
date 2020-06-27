import express from 'express';
import neo4jRoutes from './neo4j';
import repoRoutes from './repository';

const router = express.Router();

router.use('/integrated', neo4jRoutes);
router.use('/repository', repoRoutes);

export default router;
