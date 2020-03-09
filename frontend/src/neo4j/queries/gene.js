import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getGene = async (id, v) => {
  const statement = `
MATCH (g:Gene)-[:V${v}]-(gs:GeneState)
WHERE g.id="${id}"
MATCH (g)-[:V${v}]-(r:Reaction)-[metaboliteEdge:V${v}]-(m:Metabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
MATCH (r)-[:V${v}]-(rs:ReactionState)
MATCH (m)-[:V${v}]-(ms:MetaboliteState)
OPTIONAL MATCH (r)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (g)-[:V${v}]-(e:ExternalDb)
RETURN gs {
  id: g.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  externalDbs: COLLECT(DISTINCT(e)),
  reactions: COLLECT(DISTINCT(rs {id: r.id, compartmentId: c.id, subsystemId: s.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, outgoing: startnode(metaboliteEdge)=m, .*}))
} AS gene
`;

  const response = await postStatement(statement);
  const gene = handleSingleResponse(response);
  return { ...gene, externalDbs: reformatExternalDbs(gene.externalDbs) };
};


export default getGene;
