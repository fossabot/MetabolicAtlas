import express from 'express'
import { getReaction } from '../neo4j/index.js'

const neo4jRoutes = express.Router()

neo4jRoutes.get('/:version/reactions/:id', async (req, res) => {
  const { id, version } = req.params
  try {
    const reaction = await getReaction({ id, version })
    res.json(reaction)
  } catch (e) {
    res.status(400).send(e)
  }
})

export default neo4jRoutes
