import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getGene = async (id, v) => {
  const statement = `
MATCH (g:Gene)-[:V${v}]-(gs:GeneState)
WHERE g.id="${id}"
MATCH (g)-[:V${v}]-(:Reaction)-[:V${v}]-(:Metabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
OPTIONAL MATCH (g)-[:V${v}]-(:Reaction)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (g)-[:V${v}]-(e:ExternalDb)
RETURN gs {
  id: g.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  externalDbs: COLLECT(DISTINCT(e)),
} AS gene
`;

  const response = await postStatement(statement);
  const gene = handleSingleResponse(response);
  return { ...gene, externalDbs: reformatExternalDbs(gene.externalDbs) };
};


export default getGene;
