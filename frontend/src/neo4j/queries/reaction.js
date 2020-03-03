import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';

const reformat = reaction => ({
  ...reaction,
  externalDbs: reaction.externalDbs.reduce((dbs, db) => {
    let dbRefs = dbs[db.name] || [];
    dbRefs = [...dbRefs, { id: db.externalId, url: db.url }];
    return { ...dbs, [db.name]: dbRefs };
  }, {}),
});

const getReaction = async (id, v) => {
  const statement = `
MATCH (r:Reaction)-[:V${v}]-(rs:ReactionState)
WHERE r.id="${id}"
MATCH (r)-[:V${v}]-(m:Metabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
OPTIONAL MATCH (r)-[metaboliteEdge:V${v}]-(m)-[:V${v}]-(ms:MetaboliteState)
OPTIONAL MATCH (r)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (r)-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
OPTIONAL MATCH (r)-[:V${v}]-(e:ExternalDb)
OPTIONAL MATCH (r)-[:V${v}]-(p:PubmedReference)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V${v}]-(ssvg:SvgMap)
OPTIONAL MATCH (m)-[relatedEdge:V${v}]-(related:Reaction)-[:V${v}]-(relatedS:ReactionState)
RETURN rs {
  id: r.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  externalDbs: COLLECT(DISTINCT(e)),
  pubmedIds: COLLECT(DISTINCT(p)),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, outgoing: startnode(metaboliteEdge)=m, .*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {compartnmentName: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {subsystemName: ss.name, .*})),
  related: COLLECT(DISTINCT(relatedS {id: related.id, metaboliteId: m.id, outgoing: startnode(relatedEdge)=related, .*}))
} AS reaction
`;
  // TODO: try to collect m.id for related reactions

  const response = await postStatement(statement);
  const reaction = handleSingleResponse(response);
  return reformat(reaction);
};


export default getReaction;
