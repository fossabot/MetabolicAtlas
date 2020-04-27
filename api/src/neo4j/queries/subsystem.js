import querySingleResult from '../queryHandlers/single.js';
import reformatExternalDbs from '../shared/formatter.js';

const getSubsystem = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (s:Subsystem)-[:V${1}]-(r:Reaction)-[:V${1}]-(m:Metabolite)-[:V${1}]-(c:Compartment)-[:V${1}]-(cs:CompartmentState)
WHERE s.id="${id}"
MATCH (s)-[:V${1}]-(ss:SubsystemState)
MATCH (m)-[:V${1}]-(ms:MetaboliteState)
OPTIONAL MATCH (r)-[:V${1}]-(g:Gene)-[:V${1}]-(gs:GeneState)
OPTIONAL MATCH (s)-[:V${1}]-(e:ExternalDb)
OPTIONAL MATCH (c)-[:V${1}]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V${1}]-(ssvg:SvgMap)
RETURN ss {
  id: s.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  externalDbs: COLLECT(DISTINCT(e {.*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, .*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {name: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {name: ss.name, .*}))
} AS subsystem
`;
  const result = await querySingleResult(statement);
  return { ...result, externalDbs: reformatExternalDbs(result.externalDbs) };
};


export default getSubsystem;
