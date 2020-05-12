import querySingleResult from '../queryHandlers/single';

const getCompartment = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (cs:CompartmentState)-[:V${v}]-(c:Compartment)-[:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(r:Reaction)-[:V${v}]-(g:Gene)
WHERE c.id="${id}"
MATCH (r)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
RETURN cs {
  id: c.id,
  .*,
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  reactionCount: COUNT(DISTINCT(r)),
  metaboliteCount: COUNT(DISTINCT(cm)),
  geneCount: COUNT(DISTINCT(g)),
  compartmentSVGs: COLLECT(DISTINCT(csvg {name: cs.name, .*}))
} AS compartment
`;
  return querySingleResult(statement);
};


export default getCompartment;
