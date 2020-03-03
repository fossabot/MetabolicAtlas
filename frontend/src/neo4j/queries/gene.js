import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';

// TODO: in progress
const getGene = async (id, v) => {
  const statement = `
MATCH (g:Gene)-[:V${v}]-(gs:GeneState)
WHERE g.id="${id}"


MATCH (g)-[:V${v}]-(:Reaction)-[:V1]-(:Metabolite)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (g)-[:V${v}]-(:Reaction)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (g)-[:V${v}]-(e:ExternalDb)
RETURN gs {
  id: g.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  externalDbs: COLLECT(DISTINCT(e)),
} AS gene
`;

  const response = await postStatement(statement);
  return handleSingleResponse(response);
};


export default getGene;
