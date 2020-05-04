import querySingleResult from '../queryHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getReaction = async ({ id, version }) => {
  const v = version;
  const statement = `
MATCH (r:Reaction)-[cmE:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
WHERE r.id="${id}"
MATCH (r:Reaction)-[:V${v}]-(rs:ReactionState)
MATCH (cm)-[:V${v}]-(m:Metabolite)-[:V${v}]-(ms:MetaboliteState)
OPTIONAL MATCH (r)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (r)-[:V${v}]-(g:Gene)-[:V${v}]-(gs:GeneState)
OPTIONAL MATCH (r)-[:V${v}]-(e:ExternalDb)
OPTIONAL MATCH (r)-[:V${v}]-(p:PubmedReference)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V${v}]-(ssvg:SvgMap)
RETURN rs {
  id: r.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  genes: COLLECT(DISTINCT(gs {id: g.id, .*})),
  externalDbs: COLLECT(DISTINCT(e {.*})),
  pubmedIds: COLLECT(DISTINCT(p {.*})),
  metabolites: COLLECT(DISTINCT(ms {id: m.id, stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {name: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {name: ss.name, .*}))
} AS reaction
`;

  const reaction = await querySingleResult(statement);
  return { ...reaction, externalDbs: reformatExternalDbs(reaction.externalDbs) };
};


export default getReaction;
