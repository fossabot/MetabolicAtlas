import queryListResult from '../queryHandlers/list';
import reformatExternalDbs from '../shared/formatter';

const getRandomComponents = async ({ model, version }) => {
  const m = model;
  const v = version;

  const statement = `
MATCH (xs:GeneState)-[:V${v}]-(x:Gene:${m}) RETURN xs, x, labels(x), rand() as r ORDER BY r LIMIT 2
UNION
MATCH (xs:MetaboliteState)-[:V${v}]-(:Metabolite)-[:V${v}]-(x:CompartmentalizedMetabolite:${m}) RETURN xs, x, labels(x), rand() as r ORDER BY r LIMIT 2
UNION
MATCH (xs:ReactionState)-[:V${v}]-(x:Reaction:${m}) RETURN xs, x, labels(x), rand() as r ORDER BY r LIMIT 2
UNION
MATCH (xs:SubsystemState)-[:V${v}]-(x:Subsystem:${m}) RETURN xs, x, labels(x), rand() as r ORDER BY r LIMIT 2
UNION
MATCH (xs:CompartmentState)-[:V${v}]-(x:Compartment:${m}) RETURN xs, x, labels(x), rand() as r ORDER BY r LIMIT 1
`;

  return await queryListResult(statement);
};


export default getRandomComponents;
