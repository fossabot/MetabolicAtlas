import querySingleResult from 'neo4j/queryHandlers/single';

const getCompartment = async ({ id, version }) => {
  const v = version;
  const statement = `
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[:V${v}]-(c:Compartment {id: '${id}'})
  RETURN cs { id: c.id, .* } as data
  
  UNION
    
  MATCH (:Compartment {id: '${id}'})-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(:Reaction)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
  RETURN { subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
  
  UNION
  
  MATCH (:Compartment {id: '${id}'})-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(r:Reaction)
  RETURN { reactionsCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Compartment {id: '${id}'})-[:V${v}]-(cm:CompartmentalizedMetabolite)
  RETURN { metabolitesCount: COUNT(DISTINCT(cm)) } as data
  
  UNION
  
  MATCH (:Compartment {id: '${id}'})-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(:Reaction)-[:V${v}]-(g:Gene)
  RETURN { genesCount: COUNT(DISTINCT(g)) } as data
  
  UNION
  
  MATCH (:Compartment {id: '${id}'})-[:V${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (:Compartment {id: '${id}'})-[:V${v}]-(csvg:SvgMap)
  RETURN { compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as compartment
`;

  const { subsystems, compartmentSVGs, externalDbs, ...info } = await querySingleResult(statement);
  return {
    info: {
      ...info,
      subsystemCount: subsystems.length,
    },
    compartmentSVGs,
    externalDbs,
    subsystems,
  };

};


export default getCompartment;
