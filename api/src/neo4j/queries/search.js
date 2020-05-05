import queryListResult from '../queryHandlers/list';

const search = async ({ searchTerm, model, version }) => {
  const v = version ? `V${version}` : '';
  const m = model ? `:${model}` : '';

  const statement = `
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

  return queryListResult(statement);
};


export default search;
