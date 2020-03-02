import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';

const getReaction = async (id) => {
  const statement = `
MATCH (r:Reaction)-[:V1]-(rs:ReactionState)
MATCH (r)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
MATCH (r)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
MATCH (r)-[:V1]-(e:ExternalDb)
MATCH (r)-[:V1]-(p:PubmedReference)
WHERE r.id="${id}"
RETURN
  r.id as id,
  rs.reversible as reversible,
  rs.lowerBound as lowerBound,
  rs.upperBound as uppwerBound,
  rs.geneRule as geneRule,
  rs.ec as ec,
  c.id as compartmentId,
  cs.name as compartmentName,
  s.id as subsystemId,
  ss.name as subsystemName,
  e.dbName as externalDbName,
  e.url as externalDbUrl,
  e.externalId as externalDbId,
  p.pubmedId as pubmedId
`;

  const response = await postStatement(statement);
  return handleSingleResponse(response);
};

export default getReaction;
