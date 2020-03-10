import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getMetabolite = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (m:Metabolite)-[:V1]-(ms:MetaboliteState)
WHERE m.id="${id}"
MATCH (m)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (m)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
OPTIONAL MATCH (m)-[:V1]-(e:ExternalDb)
OPTIONAL MATCH (c)-[:V1]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V1]-(ssvg:SvgMap)
RETURN ms {
  id: m.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  externalDbs: COLLECT(DISTINCT(e)),
  compartmentSVGs: COLLECT(DISTINCT(csvg {compartnmentName: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {subsystemName: ss.name, .*}))
} AS metabolite
`;
  const response = await postStatement(statement);
  const metabolite = handleSingleResponse(response);
  return { ...metabolite, externalDbs: reformatExternalDbs(metabolite.externalDbs) };
};


export default metabolite;
