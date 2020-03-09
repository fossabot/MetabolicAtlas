import postStatement from '../http';
import handleSingleResponse from '../responseHandlers/single';
import reformatExternalDbs from '../shared/formatter';

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
    externalDbs: reformatExternalDbs(reaction.externalDbs),
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

const getReaction = async (id, v) => {
  const statement = `
MATCH (r:Reaction)-[:V${v}]-(rs:ReactionState)
WHERE r.id="${id}"
MATCH (r)-[:V${v}]-(m:Metabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
OPTIONAL MATCH (r)-[metaboliteEdge:V${v}]-(m)-[:V${v}]-(ms:MetaboliteState)
OPTIONAL MATCH (r)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (r)-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
OPTIONAL MATCH (r)-[:V${v}]-(e:ExternalDb)
OPTIONAL MATCH (r)-[:V${v}]-(p:PubmedReference)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V${v}]-(ssvg:SvgMap)
OPTIONAL MATCH (r)-[:V${v}]-(m)-[relatedEdge:V${v}]-(related:Reaction)-[:V${v}]-(relatedS:ReactionState)
RETURN rs {
  id: r.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  externalDbs: COLLECT(DISTINCT(e)),
  pubmedIds: COLLECT(DISTINCT(p)),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, outgoing: startnode(metaboliteEdge)=m, .*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {compartnmentName: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {subsystemName: ss.name, .*})),
  related: {
    reactions: COLLECT(DISTINCT(relatedS {id: related.id, outgoing: startnode(relatedEdge)=related, .*})),
    mappingWithMetabolites: COLLECT(DISTINCT({reactionId: related.id, metaboliteId: m.id}))
  }
} AS reaction
`;
  const response = await postStatement(statement);
  const reaction = handleSingleResponse(response);
  return reformat(reaction);
};


export default getReaction;
