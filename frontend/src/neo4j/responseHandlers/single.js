import ABBREVIATIONS from '../abbreviations';

const handleSingleResponse = (response) => {
  // TODO: add error handling
  const { data } = response;
  const result = data.results[0];
  const nodeType = ABBREVIATIONS[result.columns[0]];

  let node = result.data[0].row[0];

  result.columns.slice(1).forEach((col, i) => {
    const relatedNodeType = ABBREVIATIONS[col];
    const relatedNodeData = result.data[0].row[i + 1];

    if (relatedNodeType === `${nodeType}State`) {
      node = { ...node, ...relatedNodeData };
    } else {
      const parentNodeType = relatedNodeType.replace('State', '');
      const parentNode = node[parentNodeType];
      if (parentNode) {
        node[parentNodeType] = { ...parentNode, ...relatedNodeData };
      } else {
        node[relatedNodeType] = relatedNodeData;
      }
    }
  });

  return node;
};

export default handleSingleResponse;
