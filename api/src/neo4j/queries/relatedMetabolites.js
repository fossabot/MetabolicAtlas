import queryListResult from '../queryHandlers/list';

const getRelatedMetabolites = async ({ id, version }) => {
  const v = version;

  const statement = `
MATCH (cm:CompartmentalizedMetabolite)-[:V${v}]-(:Metabolite)-[:V${v}]-(rcm:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
WHERE cm.id="${id}"
RETURN {
  id: rcm.id,
  compartment: cs {id: c.id, .*}
} as metabolites`;

  return queryListResult(statement);
};


export default getRelatedMetabolites;
