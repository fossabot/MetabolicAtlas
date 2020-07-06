import querySingleResult from '../queryHandlers/single';

const getInteractionPartners = async ({ id, model, version }) => {
  const v = version;

  const statement = `
MATCH (comp:${model} {id: "${id}"})
WHERE comp:Gene OR comp:CompartmentalizedMetabolite

WITH CASE WHEN comp:Gene THEN 'gene' ELSE 'metabolite' END AS compType, comp

CALL apoc.when(
  comp:Gene,
  'MATCH (g:Gene {id: comp.id})-[:V${v}]-(gs:GeneState)'
  +	'RETURN {id: g.id, name: gs.name, type: compType} as component',
  'MATCH (cm:CompartmentalizedMetabolite {id: comp.id})-[:V${v}]-(:Metabolite)-[:V${v}]-(ms:MetaboliteState)'
  + ' RETURN {id: cm.id, name: ms.name, type: compType} as component',
  {comp:comp, compType:compType})
YIELD value as v

WITH v.component as component
MATCH ({id: component.id})-[:V${v}]-(r:Reaction)

CALL apoc.cypher.run("
  MATCH (:Reaction {id: $rid})-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
  RETURN { id: $rid, compartments: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
 
  UNION
 
  MATCH (:Reaction {id: $rid})-[:V${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH(s)-[:V${v}]-(ss:SubsystemState)
  RETURN { id: $rid, subsystem: COLLECT(ss.name) } as data
 
  UNION
 
  MATCH (:Reaction {id: $rid})-[:V${v}]-(g:Gene)
  WITH DISTINCT (g)
  MATCH (g)-[:V${v}]-(gs:GeneState)
  RETURN { id: $rid, genes: COLLECT(DISTINCT(gs {id: g.id, .*})) } as data
 
  UNION
 
  MATCH (:Reaction {id: $rid})-[cmE:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm, cmE
  MATCH (c:Compartment)-[:V${v}]-(cm)-[:V${v}]-(:Metabolite)-[:V${v}]-(ms:MetaboliteState)
  RETURN { id: $rid, metabolites: COLLECT(DISTINCT({id: cm.id, name: ms.name,  compartmentId: c.id, outgoing: startnode(cmE)=cm})) } as data

", {rid:r.id}) yield value
WITH apoc.map.mergeList(apoc.coll.flatten(
    apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as reaction, component
RETURN { component: component, reactions: COLLECT(reaction) }
`;

  return querySingleResult(statement);
};


export default getInteractionPartners;
