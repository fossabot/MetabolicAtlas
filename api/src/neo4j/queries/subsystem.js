import querySingleResult from '../queryHandlers/single.js';
import reformatExternalDbs from '../shared/formatter.js';

const getSubsystem = async ({ id, version }) => {
  const v = version;
  const statement = `
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[:V${v}]-(s:Subsystem {id: '${id}'})
  RETURN ss { id: s.id, .* } as data
  
  UNION
  
  MATCH (:Subsystem {id: '${id}'})-[:V${v}]-(:Reaction)-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(c:Compartment)
  WITH DISTINCT c
  MATCH (c)-[:V${v}]-(cs:CompartmentState)
  RETURN { compartments: COLLECT({id: c.id, name: cs.name}) } as data
  
  UNION
  
  MATCH (:Subsystem {id: '${id}'})-[:V${v}]-(:Reaction)-[:V${v}]-(g:Gene)
  WITH DISTINCT g
  MATCH (g)-[:V${v}]-(gs:GeneState)
  RETURN { genes: COLLECT({id: g.id, name: gs.name})[..1000] } as data
  
  UNION
  
  MATCH (:Subsystem {id: '${id}'})-[:V${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (:Subsystem {id: '${id}'})-[:V${v}]-(:Reaction)-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(:Metabolite)-[:V${v}]-(ms:MetaboliteState)
  RETURN { metabolites: COLLECT(DISTINCT(ms {id: cm.id, name: ms.name}))[..1000] }  as data
  
  UNION
  
  MATCH (:Subsystem {id: '${id}'})-[:V${v}]-(ssvg:SvgMap)
  RETURN { subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as subsystem
`;

  const result = await querySingleResult(statement);
  return { ...result, externalDbs: reformatExternalDbs(result.externalDbs) };
};


export default getSubsystem;
