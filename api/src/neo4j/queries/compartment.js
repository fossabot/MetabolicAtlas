import querySingleResult from '../queryHandlers/single';

const getCompartment = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (cs:CompartmentState)-[:V${v}]-(c:Compartment)-[:V${v}]-(cm:CompartmentalizedMetabolite)-[cmE:V${v}]-(r:Reaction)-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
WHERE c.id="${id}"
MATCH (r)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
MATCH (cm)-[:V${v}]-(:Metabolite)-[:V${v}]-(ms:MetaboliteState)
MATCH (r)-[:V${v}]-(rs:ReactionState)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
RETURN cs {
  id: c.id,
  .*,
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  reactions: COLLECT(DISTINCT(rs {id: r.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: cm.id, stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {name: cs.name, .*}))
} AS compartment
`;
  return querySingleResult(statement);
};


export default getCompartment;
