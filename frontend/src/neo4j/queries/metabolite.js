import querySingleResult from '../queryHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getMetabolite = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (m:Metabolite)-[:V${v}]-(ms:MetaboliteState)
WHERE m.id="${id}"
MATCH (m)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
OPTIONAL MATCH (m)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (m)-[:V${v}]-(e:ExternalDb)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V${v}]-(ssvg:SvgMap)
RETURN ms {
  id: m.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  externalDbs: COLLECT(DISTINCT(e {.*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {compartnmentName: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {subsystemName: ss.name, .*}))
} AS metabolite
`;
  const metabolite = await querySingleResult(statement);
  return { ...metabolite, externalDbs: reformatExternalDbs(metabolite.externalDbs) };
};


export default getMetabolite;
