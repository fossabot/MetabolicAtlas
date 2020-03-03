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
MATCH (r)-[:V1]-(:Metabolite)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (r)<-[:V1]-(re:Metabolite)-[:V1]-(res:MetaboliteState)
OPTIONAL MATCH (r)-[:V1]->(pr:Metabolite)-[:V1]-(prs:MetaboliteState)
OPTIONAL MATCH (r)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
OPTIONAL MATCH (r)-[:V1]-(g:Gene)-[:V1]-(gs:GeneState)
OPTIONAL MATCH (r)-[:V1]-(e:ExternalDb)
OPTIONAL MATCH (r)-[:V1]-(p:PubmedReference)
RETURN
  r.id as id,
  rs.reversible as reversible,
  rs.lowerBound as lowerBound,
  rs.upperBound as upperBound,
  rs.geneRule as geneRule,
  rs.ec as ec,
  COLLECT(DISTINCT({id: c.id, name: cs.name})) as compartments,
  COLLECT(DISTINCT({id: s.id, name: ss.name})) as subsystems,
  COLLECT(DISTINCT({id: g.id, name: gs.name})) as genes,
  COLLECT(DISTINCT({name: e.dbName, url: e.url, externalId: e.externalId})) as externalDbs,
  COLLECT(DISTINCT({pmid: p.pubmedId})) as pubmedIds,
  COLLECT(DISTINCT({id: re.id, name: res.name})) as reactants,
  COLLECT(DISTINCT({id: pr.id, name: prs.name})) as products
`;

  const response = await postStatement(statement);
  const reaction = handleSingleResponse(response);
  return reformat(reaction);
};


export default getReaction;
