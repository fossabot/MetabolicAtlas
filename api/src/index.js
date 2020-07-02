import express from 'express';
import router from './endpoints/index.js';

const app = express();

app.use('/api/v2', router);

app.listen(8081);
