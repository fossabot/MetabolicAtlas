import queryListResult from '../queryHandlers/list';

const search = async ({ searchTerm, model, version, limit }) => {
  const v = version ? `V${version}` : '';
  const m = model ? `:${model}` : '';

  let statement = `
CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~") YIELD node, score
WITH node, score, LABELS(node) as labelList
UNWIND labelList as labels
WITH node, score, labelList, COUNT(labels) as labelsCount
OPTIONAL MATCH (node)-[:${v}]-(parentNode${m})
RETURN DISTINCT({ node: node, labels: labelList, score: score, labelsCount: labelsCount,
	parentNode: CASE
		WHEN labelsCount > 1 THEN null
		ELSE parentNode
	END
})
`;

  if (limit) {
    statement += `LIMIT ${limit}`;
  }

  const results = await queryListResult(statement);
  // TODO: add "enum" for nodes and labels
  const collection = results.reduce((coll, r) => {
    const component = {
      ...r.node.properties,
      labels: r.parentNode ? r.parentNode.labels : r.node.labels,
    };
    console.log(component);
    return [ ...coll, component ];
    // TODO: return {} instead and namespace it by model
    return 
  }, []);

  return collection;
};


export default search;
