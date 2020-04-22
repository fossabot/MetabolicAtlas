import express from 'express'
import neo4jRoutes from './neo4j.js'

const router  = express.Router();

router.use('/integrated', neo4jRoutes)

export default router
