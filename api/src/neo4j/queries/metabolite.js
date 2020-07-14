import querySingleResult from 'neo4j/queryHandlers/single';
import reformatExternalDbs from 'neo4j/shared/formatter';

const getMetabolite = async ({ id, version }) => {
  const v = version;
  const statement = `
CALL apoc.cypher.run('
  MATCH (ms:MetaboliteState)-[:V${v}]-(:Metabolite)-[:V${v}]-(cm:CompartmentalizedMetabolite {id: "${id}"})
  RETURN ms { id: cm.id, .* } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: "${id}"})-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
  RETURN { compartment: cs { id: c.id, .* } } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: "${id}"})-[:V${v}]-(:Compartment)-[:V${v}]-(csvg:SvgMap)
  RETURN { compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: "${id}"})-[:V${v}]-(:Reaction)-[:V${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[:V${v}]-(ss:SubsystemState)
  RETURN { subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: "${id}"})-[:V${v}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:V${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: "${id}"})-[:V${v}]-(:Reaction)-[:V${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[:V${v}]-(ssvg:SvgMap)
  RETURN { subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
', {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as metabolite
`;
  const metabolite = await querySingleResult(statement);
  return { ...metabolite, externalDbs: reformatExternalDbs(metabolite.externalDbs) };
};


export default getMetabolite;
