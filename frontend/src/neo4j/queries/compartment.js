import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';

const getCompartment = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (cs:CompartmentState)-[:V${v}]-(c:Compartment)-[:V${v}]-(m:Metabolite)-[:V${v}]-(r:Reaction)-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
WHERE c.id="${id}"
MATCH (r)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
MATCH (m)-[:V${v}]-(ms:MetaboliteState)
MATCH (r)-[:V${v}]-(rs:ReactionState)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
RETURN cs {
  id: c.id,
  .*,
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  reactions: COLLECT(DISTINCT(rs {id: r.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {compartnmentName: cs.name, .*}))
} AS compartment
`;
  const response = await postStatement(statement);
  const compartment = handleSingleResponse(response);
  return compartment;
};


export default getCompartment;
