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
RETURN r, rs, c, cs, s, ss, e, p
`;

  const response = await postStatement(statement);
  return handleSingleResponse(response);
};

export default getReaction;
