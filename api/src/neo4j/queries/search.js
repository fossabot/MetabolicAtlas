import queryListResult from '../queryHandlers/list';

const componentTypes = [
  "CompartmentalizedMetabolite",
  "Metabolite",
  "Gene",
  "Reaction",
  "Subsystem",
  "Compartment",
];

const intersect = (a, b) => [...new Set(a)].filter(x => new Set(b).has(x));

const fetchCompartmentalizedMetabolites = async ({ ids, version, limit, viaMetabolties }) => {
  if (!ids) {
    return null;
  }

  let statement = ``;

  if (viaMetabolties) {
    statement += `
WITH ${JSON.stringify(ids)} as mids
UNWIND mids as mid
MATCH (:Metabolite {id:mid})-[:${version}]-(cm:CompartmentalizedMetabolite)
WITH DISTINCT(cm.id) as cmid
`;
  } else {
    statement += `
WITH ${JSON.stringify(ids)} as cmids
UNWIND cmids as cmid
`;
  }

  statement +=`
CALL apoc.cypher.run('
  MATCH (ms:MetaboliteState)-[:${version}]-(:Metabolite)-[:${version}]-(:CompartmentalizedMetabolite {id: $cmid})
  RETURN ms { id: $cmid, .* } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: $cmid})-[:${version}]-(c:Compartment)-[:${version}]-(cs:CompartmentState)
  RETURN { id: $cmid, compartment: cs { id: c.id, .* } } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: $cmid})-[:${version}]-(:Reaction)-[:${version}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[:${version}]-(ss:SubsystemState)
  RETURN { id: $cmid, subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
', {cmid:cmid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as metabolites
  LIMIT ${limit}
`;

  const start = new Date().getTime();
  const results = await queryListResult(statement);
  const elapsed = new Date().getTime() - start;
  console.log(`Time taken to fetch compartmentalized metabolites${ viaMetabolties ? " via metabolites" : ""}: ${elapsed}ms`);
  return results;
};


const fetchGenes = async ({ ids, version }) => {
  if (!ids) {
    return null;
  }

  const statement = `
WITH ${JSON.stringify(ids)} as gids
UNWIND gids as gid
CALL apoc.cypher.run("
  MATCH (gs:GeneState)-[:${version}]-(:Gene {id: $gid})
  RETURN { id: $gid, name: gs.name } as data
  
  UNION
  
  MATCH (:Gene {id: $gid})-[:${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${version}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[:${version}]-(ss:SubsystemState)
  RETURN { id: $gid, subsystems: COLLECT(DISTINCT({ id: s.id, name: ss.name })) } as data
  
  UNION
  
  MATCH (:Gene {id: $gid})-[:${version}]-(:Reaction)-[:${version}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:${version}]-(c:Compartment)-[:${version}]-(cs:CompartmentState)
  RETURN { id: $gid, compartments: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {gid:gid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as gene
`;

  const start = new Date().getTime();
  const results = await queryListResult(statement);
  const elapsed = new Date().getTime() - start;
  console.log(`Time taken to fetch genes: ${elapsed}ms`);
  return results;
};


const fetchReactions = async ({ ids, version }) => {
  if (!ids) {
    return null;
  }

  const statement = `
WITH ${JSON.stringify(ids)} as rids
UNWIND rids as rid
CALL apoc.cypher.run("
  MATCH (rs:ReactionState)-[:${version}]-(:Reaction {id: $rid})
  RETURN rs { id: $rid, .* } as data
  
  UNION
  
  MATCH (:Reaction {id: $rid})-[:${version}]-(s:Subsystem)-[:${version}]-(ss:SubsystemState)
  RETURN { id: $rid, subsystems: COLLECT(DISTINCT({ id: s.id, name: ss.name })) } as data
  
  UNION
  
  MATCH (:Reaction {id: $rid})-[:${version}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:${version}]-(c:Compartment)-[:${version}]-(cs:CompartmentState)
  RETURN { id: $rid, compartments: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {rid:rid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as reaction
`;

  const start = new Date().getTime();
  const results = await queryListResult(statement);
  const elapsed = new Date().getTime() - start;
  console.log(`Time taken to fetch reactions: ${elapsed}ms`);
  return results;
};

const fetchSubsystems = async ({ ids, version }) => {
  if (!ids) {
    return null;
  }

  const statement = `
WITH ${JSON.stringify(ids)} as sids
UNWIND sids as sid
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[:${version}]-(:Subsystem {id: $sid})
  RETURN { id: $sid, name: ss.name } as data
  
  UNION
  
  MATCH (:Subsystem {id: $sid})-[:${version}]-(r:Reaction)
  RETURN { id: $sid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Subsystem {id: $sid})-[:${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${version}]-(cm:CompartmentalizedMetabolite)
  RETURN { id: $sid, compartmentalizedMetaboliteCount: COUNT(DISTINCT cm) } as data
  
  UNION
  
  MATCH (:Subsystem {id: $sid})-[:${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${version}]-(g:Gene)
  RETURN { id: $sid, geneCount: COUNT(DISTINCT g) } as data
  
  UNION
  
  MATCH (:Subsystem {id: $sid})-[:${version}]-(:Reaction)-[:${version}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:${version}]-(c:Compartment)-[:${version}]-(cs:CompartmentState)
  RETURN { id: $sid, compartments: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {sid:sid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as subsystem
`;

  const start = new Date().getTime();
  const results = await queryListResult(statement);
  const elapsed = new Date().getTime() - start;
  console.log(`Time taken to fetch subsystems: ${elapsed}ms`);
  return results;
};

const fetchCompartments = async ({ ids, version }) => {
  if (!ids) {
    return null;
  }

  const statement = `
WITH ${JSON.stringify(ids)} as cids
UNWIND cids as cid
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[:${version}]-(:Compartment {id: $cid})
  RETURN cs { id: $cid, .* } as data
  
  UNION
  
  MATCH (:Compartment {id: $cid})-[:${version}]-(:CompartmentalizedMetabolite)-[:${version}]-(r:Reaction)
  RETURN { id: $cid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Compartment {id: $cid})-[:${version}]-(cm:CompartmentalizedMetabolite)
  RETURN { id: $cid, compartmentalizedMetaboliteCount: COUNT(DISTINCT cm) } as data
  
  UNION
  
  MATCH (:Compartment {id: $cid})-[:${version}]-(:CompartmentalizedMetabolite)-[:${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${version}]-(g:Gene)
  RETURN { id: $cid, geneCount: COUNT(DISTINCT g) } as data
  
  UNION
  
  MATCH (:Compartment {id: $cid})-[:${version}]-(:CompartmentalizedMetabolite)-[:${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${version}]-(s:Subsystem)
  RETURN { id: $cid, subsystemCount: COUNT(DISTINCT s) } as data
", {cid:cid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as compartment
`;

  const start = new Date().getTime();
  const results = await queryListResult(statement);
  const elapsed = new Date().getTime() - start;
  console.log(`Time taken to fetch compartments: ${elapsed}ms`);
  return results;
};

/*
 * The search consists of two steps
 * 1. Do a fuzzy search over all nodes covered by full-text search index
 * 2. Fetch results for each component type (parallelly) and return result
 */
const search = async ({ searchTerm, model, version, limit }) => {
  const v = version ? `V${version}` : '';
  const m = model ? `:${model}` : '';
  const l = limit || 50;

  // Metabolites are not included as it would mess with the limit and
  // relevant metabolites should be matched through CompartmentalizedMetabolites
  const statement = `
CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~")
YIELD node, score
WITH node, score, LABELS(node) as labelList
UNWIND labelList as labels
WITH node, score, labelList, COUNT(labels) as labelsCount
OPTIONAL MATCH (node)-[:${v}]-(parentNode${m})
RETURN DISTINCT(
	CASE
		WHEN EXISTS(node.id) THEN { id: node.id, labels: labelList, score: score }
		ELSE { id: parentNode.id, labels: LABELS(parentNode), score: score }
	END
)
LIMIT ${l}
`;

  const start = new Date().getTime();
  const results = await queryListResult(statement);

  const uniqueIds = results.reduce((o, r) => {
    const c = intersect(componentTypes, r.labels);
    if (!o[c]) {
      o[c] = new Set();
    }
    o[c].add(r.id);
    return o;
  }, {});

  const ids = Object.assign({}, ...Object.keys(uniqueIds).map(c => ({[c]: Array.from(uniqueIds[c]) })));

  const [
    compartmentalizedMetabolites,
    metabolites,
    genes,
    reactions,
    subsystems,
    compartments,
  ] = await Promise.all([
    fetchCompartmentalizedMetabolites({ ids: ids["CompartmentalizedMetabolite"], version: v, limit: l }),
    fetchCompartmentalizedMetabolites({ ids: ids["Metabolite"], version: v, limit: l,  viaMetabolties: true }),
    fetchGenes({ ids: ids["Gene"], version: v }),
    fetchReactions({ ids: ids["Reaction"], version: v }),
    fetchSubsystems({ ids: ids["Subsystem"], version: v }),
    fetchCompartments({ ids: ids["Compartment"], version: v }),
  ]);

  const elapsed = new Date().getTime() - start;
  console.log(`Time taken to perform search: ${elapsed}ms`);

  // formatting for simple (gem browser) search
  return {
    human1: {
      metabolite: [...compartmentalizedMetabolites || [], ...metabolites || []].map(m => ({ ...m, compartment: m.compartment.name })),
      gene: genes,
      reaction: reactions,
      subsystem: subsystems,
      compartment: compartments,
    }
  };
};


export default search;
