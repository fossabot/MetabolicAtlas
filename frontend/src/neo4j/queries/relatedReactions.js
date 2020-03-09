import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';

const reformat = (reaction) => {
  const relatedReactionsMetaboliteIds = {};

  reaction.related.mappingWithMetabolites.forEach((mapping) => {
    if (relatedReactionsMetaboliteIds[mapping.reactionId]) {
      relatedReactionsMetaboliteIds[mapping.reactionId] = [
        ...relatedReactionsMetaboliteIds[mapping.reactionId],
        mapping.metaboliteId,
      ];
    } else {
      relatedReactionsMetaboliteIds[mapping.reactionId] = [mapping.metaboliteId];
    }
  });

  return {
    ...reaction,
    related: reaction.related.reactions.map(r => ({
      ...r,
      metaboliteIds: relatedReactionsMetaboliteIds[r.id],
    })).sort((r1, r2) => { // order by related metabolites count, highest to lowest
      if (r1.metaboliteIds.length === r2.metaboliteIds.length) {
        return 0;
      }
      return r1.metaboliteIds.length > r2.metaboliteIds.length ? -1 : 1;
    }),
  };
};

const NODE_TYPES = {
  reaction: 'Reaction',
  gene: 'Gene',
  metabolite: 'Metabolite',
  subsystem: 'Subsystem',
  compartment: 'Compartment'
};

const getRelatedReaction = async ({ nodeType, id, version }) => {
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
OPTIONAL MATCH (related)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
OPTIONAL MATCH (related)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (related)-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
RETURN relatedS {
  id: related.id,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, outgoing: startnode(metaboliteEdge)=m, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*}))
} as reactions
`;

  const response = await postStatement(statement);
  const reaction = handleSingleResponse(response);
  return reformat(reaction);
};

/*

// Reaction
TODO: remove relatedEdge and add metaboliteEdge as above
  `
MATCH (x:Reaction)-[:V1]-(m:Metabolite)
WHERE x.id=""
MATCH (x)-[:V1]-(m)-[relatedEdge:V1]-(related:Reaction)-[:V1]-(relatedS:ReactionState)
MATCH (m)-[:V1]-(ms:MetaboliteState)
OPTIONAL MATCH (related)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (related)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
OPTIONAL MATCH (related)-[:V1]-(g:Gene)-[:V1]-(gs:GeneState)
RETURN relatedS {
  id: related.id,
  outgoing: startnode(relatedEdge)=related,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*}))
} as reactions
`;



// Gene
  `
MATCH (x:Gene)-[relatedEdge:V1]-(related:Reaction)-[:V1]-(m:Metabolite)
WHERE x.id=""
MATCH (related)-[:V1]-(relatedS:ReactionState)
MATCH (m)-[:V1]-(ms:MetaboliteState)
OPTIONAL MATCH (related)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (related)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
OPTIONAL MATCH (related)-[:V1]-(g:Gene)-[:V1]-(gs:GeneState)
RETURN relatedS {
  id: related.id,
  outgoing: startnode(relatedEdge)=related,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*}))
} as reactions
`;



// Metabolite
  `
MATCH (x:Metabolite)-[relatedEdge:V1]-(related:Reaction)
WHERE x.id=""
MATCH (related)-[:V1]-(relatedS:ReactionState)
MATCH (related)-[:V1]-(m:Metabolite)-[:V1]-(ms:MetaboliteState)
OPTIONAL MATCH (related)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (related)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
OPTIONAL MATCH (related)-[:V1]-(g:Gene)-[:V1]-(gs:GeneState)
RETURN relatedS {
  id: related.id,
  outgoing: startnode(relatedEdge)=related,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*}))
} as reactions
`;





// Subsystem
  `
MATCH (x:Subsystem)-[relatedEdge:V1]-(related:Reaction)-[:V1]-(m:Metabolite)
WHERE x.id=""
MATCH (related)-[:V1]-(relatedS:ReactionState)
MATCH (m)-[:V1]-(ms:MetaboliteState)
OPTIONAL MATCH (related)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (related)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
OPTIONAL MATCH (related)-[:V1]-(g:Gene)-[:V1]-(gs:GeneState)
RETURN relatedS {
  id: related.id,
  outgoing: startnode(relatedEdge)=related,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*}))
} as reactions
`;



// Compartment
  `
MATCH (x:Compartment)-[:V1]-(m:Metabolite)-[relatedEdge:V1]-(related:Reaction)
WHERE x.id=""
MATCH (related)-[:V1]-(relatedS:ReactionState)
MATCH (m)-[:V1]-(ms:MetaboliteState)
OPTIONAL MATCH (related)-[:V1]-(c:Compartment)-[:V1]-(cs:CompartmentState)
OPTIONAL MATCH (related)-[:V1]-(s:Subsystem)-[:V1]-(ss:SubsystemState)
OPTIONAL MATCH (related)-[:V1]-(g:Gene)-[:V1]-(gs:GeneState)
RETURN relatedS {
  id: related.id,
  outgoing: startnode(relatedEdge)=related,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*}))
} as reactions
`;





RETURN {
  reactions: relatedS {
    id: related.id,
    outgoing: startnode(relatedEdge)=related,
    compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
    subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
    metabolites: COLLECT(DISTINCT(ms {id: m.id, .*})),
    genes: COLLECT(DISTINCT(gs {id: g.id, .*}))
  },
  mappingWithMetabolites: COLLECT(DISTINCT({reactionId: related.id, metaboliteId: m.id}))
} as relatedReactions
*/

export default getReaction;
