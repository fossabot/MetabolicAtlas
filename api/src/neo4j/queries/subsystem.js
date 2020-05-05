import querySingleResult from '../queryHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getSubsystem = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (ss:SubsystemState)-[:V${v}]-(s:Subsystem)-[:V${v}]-(r:Reaction)-[cmE:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
WHERE s.id="${id}"
MATCH (cm)-[:V${v}]-(:Metabolite)-[:V${v}]-(ms:MetaboliteState)
OPTIONAL MATCH (r)-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
OPTIONAL MATCH (s)-[:V${v}]-(e:ExternalDb)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V${v}]-(ssvg:SvgMap)
RETURN ss {
  id: s.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  externalDbs: COLLECT(DISTINCT(e {.*})),
  metabolites: COLLECT(DISTINCT(ms {id: cm.id, stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {name: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {name: ss.name, .*}))
} AS subsystem
`;

  console.log(statement);
  const result = await querySingleResult(statement);
  return { ...result, externalDbs: reformatExternalDbs(result.externalDbs) };
};


export default getSubsystem;
