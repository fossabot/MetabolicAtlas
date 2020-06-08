import queryListResult from '../queryHandlers/list';

const NODE_TYPES = {
  reaction: 'Reaction',
  gene: 'Gene',
  metabolite: 'Metabolite',
  subsystem: 'Subsystem',
  compartment: 'Compartment',
};

// TODO: add pagination and search
const getRelatedReactions = async ({ nodeType, id, version }) => {
  const v = version;
  let statement;

  switch (nodeType) {
    case NODE_TYPES.reaction:
      statement = `
MATCH (r1:Reaction {id: '${id}'})-[cms1:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(m:Metabolite)
WITH r1, count(cms1) as ccms1, collect(distinct(m)) as ms
UNWIND ms as m
MATCH (m)-[:V${v}]-(:CompartmentalizedMetabolite)-[cms2:V${v}]-(r:Reaction)
WITH r1, r, count(cms2) as ccms2, ccms1
WHERE ccms1 = ccms2
MATCH (r)-[cms3:V${v}]-(:CompartmentalizedMetabolite)
WITH ccms1, count(cms3) as ccms3, r1, r
WHERE ccms1 = ccms3 and r1.id <> r.id`;
      break;
    case NODE_TYPES.gene:
      statement = `
MATCH (:Gene {id: '${id}'})-[:V${v}]-(r:Reaction)`;
      break;
    case NODE_TYPES.metabolite:
      statement = `
MATCH (:CompartmentalizedMetabolite {id: '${id}'})-[:V${v}]-(r:Reaction)`;
      break;
    case NODE_TYPES.subsystem:
      statement = `
MATCH (:Subsystem {id: '${id}'})-[:V${v}]-(r:Reaction)`;
      break;
    case NODE_TYPES.compartment:
      statement = `
MATCH (:Compartment {id: '${id}'})-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(r:Reaction)`;
      break;
    default:
      throw new Error(`Unrecognized node type: ${nodeType}`);
  }

  statement += `
WITH r.id as rid
LIMIT 100
CALL apoc.cypher.run("
  MATCH (rs:ReactionState)-[:V${v}]-(r:Reaction {id: $rid})
  RETURN rs { id: $rid, .* } as data
 
  UNION
 
  MATCH (r:Reaction {id: $rid})-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
  RETURN { id: $rid, compartments: COLLECT(DISTINCT(cs {id: c.id, .*})) } as data
 
  UNION
 
  MATCH (r:Reaction {id: $rid})-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
  RETURN { id: $rid, subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})) } as data
 
  UNION
 
  MATCH (r:Reaction {id: $rid})-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
  RETURN { id: $rid, genes: COLLECT(DISTINCT(gs {id: g.id, .*})) } as data
 
  UNION
 
  MATCH (r:Reaction {id: $rid})-[cmE:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(:Metabolite)-[:V${v}]-(ms:MetaboliteState)
  RETURN { id: $rid, metabolites: COLLECT(DISTINCT(ms {id: cm.id, stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})) } as data
", {rid:rid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
    apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as reactions
`;

  return queryListResult(statement);
};


const getRelatedReactionsForReaction = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.reaction,
  });

const getRelatedReactionsForGene = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.gene,
  });

const getRelatedReactionsForMetabolite = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.metabolite,
  });

const getRelatedReactionsForSubsystem = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.subsystem,
  });

const getRelatedReactionsForCompartment = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.compartment,
  });

export {
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
};