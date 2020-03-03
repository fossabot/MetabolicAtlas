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

const getReaction = async (id) => {
  const statement = `
MATCH (r:Reaction)-[:V1]-(rs:ReactionState)
WHERE r.id="${id}"
MATCH (r)-[:V1]-(m:Metabolite)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (r)-[metaboliteEdge:V1]-(m)-[:V1]-(ms:MetaboliteState)
OPTIONAL MATCH (r)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
OPTIONAL MATCH (r)-[:V1]-(g:Gene)-[:V1]-(gs:GeneState)
OPTIONAL MATCH (r)-[:V1]-(e:ExternalDb)
OPTIONAL MATCH (r)-[:V1]-(p:PubmedReference)
OPTIONAL MATCH (c)-[:V1]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V1]-(ssvg:SvgMap)
OPTIONAL MATCH (r)-[:V1]-(m)-[relatedEdge:V1]-(related:Reaction)-[:V1]-(relatedS:ReactionState)
RETURN rs {
  id: r.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  externalDbs: COLLECT(DISTINCT(e)),
  pubmedIds: COLLECT(DISTINCT(p)),
  metabolites: COLLECT(DISTINCT({id: m.id, outgoing: startnode(metaboliteEdge)=m, name: ms.name})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {compartnmentName: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {subsystemName: ss.name, .*})),
  related: COLLECT(DISTINCT(relatedS {id: related.id, outgoing: startnode(relatedEdge)=related, .*}))
} AS reaction
`;

  const response = await postStatement(statement);
  const reaction = handleSingleResponse(response);
  return reformat(reaction);
};


export default getReaction;
