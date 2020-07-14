import queryListResult from 'neo4j/queryHandlers/list';

const getRelatedMetabolites = async ({ id, version }) => {
  const v = version;

  const statement = `
MATCH (cm:CompartmentalizedMetabolite)-[:V${v}]-(m:Metabolite)-[:V${v}]-(rcm:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
WHERE cm.id="${id}"
MATCH (m)-[:V${v}]-(ms:MetaboliteState)
RETURN {
  id: rcm.id,
  fullName: COALESCE(ms.name, '') + ' [' + COALESCE(cs.letterCode, '') + ']',
  compartment: cs {
    id: c.id, 
    .*
  }
} as metabolites`;

  return queryListResult(statement);
};


export default getRelatedMetabolites;
