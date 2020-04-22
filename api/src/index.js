import express from 'express'
import router from './endpoints/index.js'

const app = express()

app.use('/new_api', router)

app.listen(8081)
