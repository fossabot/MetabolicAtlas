import neo4j from 'neo4j-driver';

const uri = 'bolt://neo4j';
const driver = neo4j.driver(uri);

process.on('exit', async () => {
  await driver.close();
});

export default driver;
