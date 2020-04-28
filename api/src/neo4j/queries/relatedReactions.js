import queryListResult from '../queryHandlers/list';

const NODE_TYPES = {
  reaction: 'Reaction',
  gene: 'Gene',
  metabolite: 'Metabolite',
  subsystem: 'Subsystem',
  compartment: 'Compartment',
};

// TODO: add pagination and search
const getRelatedReactions = async ({ nodeType, id, version }) => {
  const v = version;
  let statement;

  switch (nodeType) {
    case NODE_TYPES.reaction:
      statement = `
MATCH (x:Reaction)-[:V${v}]-(m:Metabolite)
WHERE x.id="${id}"
MATCH (x)-[:V${v}]-(m)-[metaboliteEdge:V${v}]-(related:Reaction)-[:V${v}]-(relatedS:ReactionState)
MATCH (m)-[:V${v}]-(ms:MetaboliteState)`;
      break;
    case NODE_TYPES.gene:
      statement = `
MATCH (x:Gene)-[:V${v}]-(related:Reaction)-[metaboliteEdge:V${v}]-(m:Metabolite)
WHERE x.id="${id}"
MATCH (related)-[:V${v}]-(relatedS:ReactionState)
MATCH (m)-[:V${v}]-(ms:MetaboliteState)`;
      break;
    case NODE_TYPES.metabolite:
      statement = `
MATCH (x:Metabolite)-[:V${v}]-(related:Reaction)
WHERE x.id="${id}"
MATCH (related)-[:V${v}]-(relatedS:ReactionState)
MATCH (related)-[metaboliteEdge:V${v}]-(m:Metabolite)-[:V${v}]-(ms:MetaboliteState)`;
      break;
    case NODE_TYPES.subsystem:
      statement = `
MATCH (x:Subsystem)-[:V${v}]-(related:Reaction)-[metaboliteEdge:V${v}]-(m:Metabolite)
WHERE x.id="${id}"
MATCH (related)-[:V${v}]-(relatedS:ReactionState)
MATCH (m)-[:V${v}]-(ms:MetaboliteState)`;
      break;
    case NODE_TYPES.compartment:
      statement = `
MATCH (x:Compartment)-[:V${v}]-(m:Metabolite)-[metaboliteEdge:V${v}]-(related:Reaction)
WHERE x.id="${id}"
MATCH (related)-[:V${v}]-(relatedS:ReactionState)
MATCH (m)-[:V${v}]-(ms:MetaboliteState)`;
      break;
    default:
      throw new Error(`Unrecognized node type: ${nodeType}`);
  }

  statement += `
OPTIONAL MATCH (m)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
OPTIONAL MATCH (related)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (related)-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
RETURN relatedS {
  id: related.id,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, stoichiometry: metaboliteEdge.stoichiometry, outgoing: startnode(metaboliteEdge)=m, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*}))
} as reactions
`;

  return queryListResult(statement);
};

const getRelatedReactionsForReaction = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.reaction,
});

const getRelatedReactionsForGene = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.gene,
});

const getRelatedReactionsForMetabolite = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.metabolite,
});

const getRelatedReactionsForSubsystem = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.subsystem,
});

const getRelatedReactionsForCompartment = ({ id, version }) => getRelatedReactions({
  id, version, nodeType: NODE_TYPES.compartment,
});

export {
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
};
