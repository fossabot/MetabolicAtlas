import querySingleResult from '../queryHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getMetabolite = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (ms:MetaboliteState)-[:V${v}]-(m:Metabolite)-[:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
WHERE cm.id="${id}"
OPTIONAL MATCH (m)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (m)-[:V${v}]-(e:ExternalDb)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V${v}]-(ssvg:SvgMap)
RETURN ms {
  id: cm.id,
  .*,
  compartment: cs {id: c.id, .*},
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  externalDbs: COLLECT(DISTINCT(e {.*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {name: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {name: ss.name, .*}))
} AS metabolite
`;
  const metabolite = await querySingleResult(statement);
  return { ...metabolite, externalDbs: reformatExternalDbs(metabolite.externalDbs) };
};


export default getMetabolite;
