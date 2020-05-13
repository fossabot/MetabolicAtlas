import querySingleResult from '../queryHandlers/single';
import reformatExternalDbs from '../shared/formatter';

const getGene = async ({ id, version }) => {
  const v = version;

  const statement = `
MATCH (gs:GeneState)-[:V${v}]-(g:Gene)-[:V${v}]-(r:Reaction)-[cmE:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
WHERE g.id="${id}"
MATCH (cm)-[:V${v}]-(:Metabolite)-[:V${v}]-(ms:MetaboliteState)
MATCH (g)-[:V${v}]-(r:Reaction)-[cmE:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)-[:V${v}]-(cs:CompartmentState)
MATCH (r)-[:V${v}]-(rs:ReactionState)
OPTIONAL MATCH (r)-[:V${v}]-(s:Subsystem)-[:V${v}]-(ss:SubsystemState)
OPTIONAL MATCH (g)-[:V${v}]-(e:ExternalDb)
OPTIONAL MATCH (c)-[:V${v}]-(csvg:SvgMap)
OPTIONAL MATCH (s)-[:V${v}]-(ssvg:SvgMap)
RETURN gs {
  id: g.id,
  .*,
  compartments: COLLECT(DISTINCT(cs {id: c.id, .*})),
  subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})),
  externalDbs: COLLECT(DISTINCT(e {.*})),
  metabolites: COLLECT(DISTINCT(ms {id: cm.id, stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})),
  compartmentSVGs: COLLECT(DISTINCT(csvg {name: cs.name, .*})),
  subsystemSVGs: COLLECT(DISTINCT(ssvg {name: ss.name, .*}))
} AS gene
`;

  const gene = await querySingleResult(statement);
  return { ...gene, externalDbs: reformatExternalDbs(gene.externalDbs) };
};


export default getGene;
