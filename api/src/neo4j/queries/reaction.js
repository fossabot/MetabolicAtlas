import querySingleResult from '../queryHandlers/single.js';
import reformatExternalDbs from '../shared/formatter.js';

const getReaction = async ({ id, version }) => {
  const v = version;
  const statement = `
CALL apoc.cypher.run("
  MATCH (rs:ReactionState)-[:V${v}]-(r:Reaction {id: '${id}'})
  RETURN rs { id: r.id, .* } as data
  
  UNION
  
  MATCH (r:Reaction {id: '${id}'})-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
  RETURN { compartments: COLLECT(DISTINCT(cs {id: c.id, .*})) } as data
  
  UNION
  
  MATCH (r:Reaction {id: '${id}'})-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
  RETURN { subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})) } as data
  
  UNION
  
  MATCH (r:Reaction {id: '${id}'})-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
  RETURN { genes: COLLECT(DISTINCT(gs {id: g.id, .*})) } as data
  
  UNION
  
  MATCH (r:Reaction {id: '${id}'})-[cmE:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(:Metabolite)-[:V${v}]-(ms:MetaboliteState)
  MATCH (cm)-[:V${v}]-(:Compartment)-[:V${v}]-(cs:CompartmentState)
  RETURN { metabolites: COLLECT(DISTINCT(ms {id: cm.id, compartment: cs.name, fullName: COALESCE(ms.name, '') + ' [' + COALESCE(cs.letterCode, '') + ']', stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})) } as data
  
  UNION
  
  MATCH (r:Reaction {id: '${id}'})-[:V${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (r:Reaction {id: '${id}'})-[:V${v}]-(p:PubmedReference)
  RETURN { pubmedIds: COLLECT(DISTINCT(p {.*})) } as data
  
  UNION
  
  MATCH (r:Reaction {id: '${id}'})-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(:Compartment)-[:V${v}]-(csvg:SvgMap)
  RETURN { compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
  
  UNION
  
  MATCH (r:Reaction {id: '${id}'})-[:V${v}]-(:Subsystem)-[:V${v}]-(ssvg:SvgMap)
  RETURN { subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as reaction
`;

  const reaction = await querySingleResult(statement);
  return { ...reaction, externalDbs: reformatExternalDbs(reaction.externalDbs) };
};

export default getReaction;
