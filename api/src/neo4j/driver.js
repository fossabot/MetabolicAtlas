import neo4j from 'neo4j-driver'

// TODO: put uri in an environment variable
const uri = 'bolt://neo4j'
const driver = neo4j.driver(uri)

process.on('exit', async () => {
  console.info('closing neo4j driver')
  await driver.close()
})

export default driver
