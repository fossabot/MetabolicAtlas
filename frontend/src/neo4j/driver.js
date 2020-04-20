import * as neo4j from 'neo4j-driver';

// TODO: put uri in an environment variable
const uri = 'neo4j://localhost';
const driver = neo4j.driver(uri);

export default driver;
