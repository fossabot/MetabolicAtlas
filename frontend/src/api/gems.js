import axios from 'axios';

const fetchGems = async () => {
  const { data } = await axios.get('gems/');
  // TODO consider moving this mapping logic into store

  return data.map((g) => {
    const gem = {
      ...g,
      ...g.sample,
      tissue: [g.sample.tissue, g.sample.cell_type, g.sample.cell_line].filter(e => e).join(' ‒ ') || '-',
      stats: `reactions:&nbsp;${g.reaction_count === null ? '-' : g.reaction_count}<br>metabolites:&nbsp;${g.metabolite_count === null ? '-' : g.metabolite_count}<br>genes:&nbsp;${g.gene_count === null ? '-' : g.gene_count}`,
      maintained: g.maintained ? 'Yes' : 'No',
      organ_system: g.sample.organ_system || '-',
      condition: g.condition || '-',
    };
    // eslint-disable-next-line
    const { sample, cell_type, reaction_count, gene_count, metabolite_count, ...strippedGem } = gem;
    return strippedGem;
  });
};

const fetchGemData = async (gemId) => {
  const { data } = await axios.get(`gems/${gemId}`);
  const gem = {
    ...data,
    ...data.sample,
    ...data.gemodelset,
    description: data.description || data.gemodelset.description,
    set_name: data.gemodelset.set_name,
    ref: data.ref.length > 0 ? data.ref : data.gemodelset.reference,
  };
  // eslint-disable-next-line
  const { id, sample, name, reference, gemodelset, ...strippedGem } = gem;

  return strippedGem;
};

export default { fetchGems, fetchGemData };
