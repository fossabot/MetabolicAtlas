import neo4j from 'neo4j-driver';

const uri = 'bolt://neo4j';
const driver = neo4j.driver(uri, null, { disableLosslessIntegers: true });
// https://github.com/neo4j/neo4j-javascript-driver#enabling-native-numbers

process.on('exit', async () => {
  await driver.close();
});

export default driver;
