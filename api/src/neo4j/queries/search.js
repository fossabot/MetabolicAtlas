import queryListResult from '../queryHandlers/list';

const search = async ({ searchTerm, model, version }) => {
  const v = version ? `V${version}` : '';
  const m = model ? `:${model}` : '';

  const statement = `
CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~") YIELD node as stateNode, score
MATCH (stateNode)-[:${v}]-(parentNode${m})
RETURN stateNode, LABELS(parentNode) as labels, parentNode.id as parentNodeId, score
`;

  return queryListResult(statement);
};


export default search;
