import express from 'express';
import router from 'endpoints/index';
import { initializeSearchIndex } from 'neo4j';
import compression from 'compression';

const app = express();

// runs only when index is not created
(async () => initializeSearchIndex())();

app.use(compression());
app.use('/api/v2', router);

app.listen(8081);
