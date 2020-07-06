import querySingleResult from '../queryHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getGene = async ({ id, version }) => {
  const v = version;

  const statement = `
CALL apoc.cypher.run("
  MATCH (gs:GeneState)-[:V${v}]-(g:Gene {id: '${id}'})
  RETURN gs { id: g.id, .* } as data
  
  UNION
  
  MATCH (:Gene {id: '${id}'})-[:V${v}]-(:Reaction)-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
  RETURN { compartments: COLLECT(DISTINCT({id: c.id, name: cs.name})) } as data
  
  UNION
  
  MATCH (:Gene {id: '${id}'})-[:V${v}]-(:Reaction)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
  RETURN { subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
  
  UNION
  
  MATCH (:Gene {id: '${id}'})-[:V${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (:Gene {id: '${id}'})-[:V${v}]-(:Reaction)-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(:Compartment)-[:V${v}]-(csvg:SvgMap)
  RETURN { compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
  
  UNION
  
  MATCH (:Gene {id: '${id}'})-[:V${v}]-(:Reaction)-[:V${v}]-(:Subsystem)-[:V${v}]-(ssvg:SvgMap)
  RETURN { subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as gene
`;

  const gene = await querySingleResult(statement);
  return { ...gene, externalDbs: reformatExternalDbs(gene.externalDbs) };
};


export default getGene;
