import queryListResult from '../queryHandlers/list';

const search = async ({ searchTerm, model, version, limit }) => {
  const v = version ? `V${version}` : '';
  const m = model ? `:${model}` : '';
  const l = limit || 50;

  let statement = `
CALL apoc.cypher.run('
  CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~")
  YIELD node
  WITH node
  
  MATCH (node:MetaboliteState)-[:${v}]-(:Metabolite${m})-[:${v}]-(cm:CompartmentalizedMetabolite)
  RETURN DISTINCT(cm.id) as cmid

  UNION

  MATCH (:MetaboliteState)-[:${v}]-(node:Metabolite${m})-[:${v}]-(cm:CompartmentalizedMetabolite)
  RETURN DISTINCT(cm.id) as cmid
', {}) yield value
WITH DISTINCT(value.cmid) as cmid
LIMIT ${l}

CALL apoc.cypher.run('
  MATCH (ms:MetaboliteState)-[:${v}]-(:Metabolite)-[:${v}]-(:CompartmentalizedMetabolite {id: $cmid})
  RETURN ms { id: $cmid, .* } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: $cmid})-[:${v}]-(c:Compartment)-[:${v}]-(cs:CompartmentState)
  RETURN { id: $cmid, compartment: cs { id: c.id, .* } } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite {id: $cmid})-[:${v}]-(:Reaction)-[:${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[:${v}]-(ss:SubsystemState)
  RETURN { id: $cmid, subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
', {cmid:cmid}) yield value
RETURN { metabolite: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as x

UNION

CALL apoc.cypher.run('
  CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~")
  YIELD node
  WITH node
  
  MATCH (node:GeneState)-[:${v}]-(g:Gene${m})
  RETURN DISTINCT(g.id) as gid

  UNION

  MATCH (:GeneState)-[:${v}]-(node:Gene${m})
  RETURN DISTINCT(node.id) as gid
', {}) yield value
WITH DISTINCT(value.gid) as gid
LIMIT ${l}

CALL apoc.cypher.run("
  MATCH (gs:GeneState)-[:${v}]-(:Gene {id: $gid})
  RETURN { id: $gid, name: gs.name } as data
  
  UNION
  
  MATCH (:Gene {id: $gid})-[:${v}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[:${v}]-(ss:SubsystemState)
  RETURN { id: $gid, subsystems: COLLECT(DISTINCT({ id: s.id, name: ss.name })) } as data
  
  UNION
  
  MATCH (:Gene {id: $gid})-[:${v}]-(:Reaction)-[:${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:${v}]-(c:Compartment)-[:${v}]-(cs:CompartmentState)
  RETURN { id: $gid, compartments: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {gid:gid}) yield value
RETURN { gene: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as x

UNION

CALL apoc.cypher.run('
  CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~")
  YIELD node
  WITH node
  
  MATCH (node:ReactionState)-[:${v}]-(r:Reaction${m})
  RETURN DISTINCT(r.id) as rid

  UNION

  MATCH (:ReactionState)-[:${v}]-(node:Reaction${m})
  RETURN DISTINCT(node.id) as rid
', {}) yield value
WITH DISTINCT(value.rid) as rid
LIMIT ${l}

CALL apoc.cypher.run("
  MATCH (rs:ReactionState)-[:${v}]-(:Reaction {id: $rid})
  RETURN rs { id: $rid, .* } as data
  
  UNION
  
  MATCH (:Reaction {id: $rid})-[:${v}]-(s:Subsystem)-[:${v}]-(ss:SubsystemState)
  RETURN { id: $rid, subsystems: COLLECT(DISTINCT({ id: s.id, name: ss.name })) } as data
  
  UNION
  
  MATCH (:Reaction {id: $rid})-[:${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:${v}]-(c:Compartment)-[:${v}]-(cs:CompartmentState)
  RETURN { id: $rid, compartments: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {rid:rid}) yield value
RETURN { reaction: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as x

UNION

CALL apoc.cypher.run('
  CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~")
  YIELD node
  WITH node
  
  MATCH (node:SubsystemState)-[:${v}]-(s:Subsystem${m})
  RETURN DISTINCT(s.id) as sid

  UNION

  MATCH (:SubsystemState)-[:${v}]-(node:Subsystem${m})
  RETURN DISTINCT(node.id) as sid
', {}) yield value
WITH DISTINCT(value.sid) as sid
LIMIT ${l}

CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[:${v}]-(:Subsystem {id: $sid})
  RETURN { id: $sid, name: ss.name } as data
  
  UNION
  
  MATCH (:Subsystem {id: $sid})-[:${v}]-(r:Reaction)
  RETURN { id: $sid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Subsystem {id: $sid})-[:${v}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${v}]-(cm:CompartmentalizedMetabolite)
  RETURN { id: $sid, compartmentalizedMetaboliteCount: COUNT(DISTINCT cm) } as data
  
  UNION
  
  MATCH (:Subsystem {id: $sid})-[:${v}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${v}]-(g:Gene)
  RETURN { id: $sid, geneCount: COUNT(DISTINCT g) } as data
  
  UNION
  
  MATCH (:Subsystem {id: $sid})-[:${v}]-(:Reaction)-[:${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:${v}]-(c:Compartment)-[:${v}]-(cs:CompartmentState)
  RETURN { id: $sid, compartments: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {sid:sid}) yield value
RETURN { subsystem: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as x

UNION

CALL apoc.cypher.run('
  CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~")
  YIELD node
  WITH node
  
  MATCH (node:CompartmentState)-[:${v}]-(c:Compartment${m})
  RETURN DISTINCT(c.id) as cid

  UNION

  MATCH (:CompartmentState)-[:${v}]-(node:Compartment${m})
  RETURN DISTINCT(node.id) as cid
', {}) yield value
WITH DISTINCT(value.cid) as cid
LIMIT ${l}

CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[:${v}]-(:Compartment {id: $cid})
  RETURN cs { id: $cid, .* } as data
  
  UNION
  
  MATCH (:Compartment {id: $cid})-[:${v}]-(:CompartmentalizedMetabolite)-[:${v}]-(r:Reaction)
  RETURN { id: $cid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Compartment {id: $cid})-[:${v}]-(cm:CompartmentalizedMetabolite)
  RETURN { id: $cid, compartmentalizedMetaboliteCount: COUNT(DISTINCT cm) } as data
  
  UNION
  
  MATCH (:Compartment {id: $cid})-[:${v}]-(:CompartmentalizedMetabolite)-[:${v}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${v}]-(g:Gene)
  RETURN { id: $cid, geneCount: COUNT(DISTINCT g) } as data
  
  UNION
  
  MATCH (:Compartment {id: $cid})-[:${v}]-(:CompartmentalizedMetabolite)-[:${v}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[:${v}]-(s:Subsystem)
  RETURN { id: $cid, subsystemCount: COUNT(DISTINCT s) } as data
", {cid:cid}) yield value
RETURN { compartment: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as x
`;

  const results = await queryListResult(statement);

  const formattedResults = results.reduce((r, c) => {
    const [k, v] = Object.entries(c)[0];
    r[k] = [...r[k], v];
    return r;
  }, {
    metabolite: [],
    gene: [],
    reaction: [],
    subsystem: [],
    compartment: []
  });

  return formattedResults;
};


export default search;
