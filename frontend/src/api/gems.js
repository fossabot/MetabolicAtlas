import axios from 'axios';

const gemsDict = {};

const fetchGems = async () => {
  const { data } = await axios({ url: 'models/', baseURL: '/new_api/repository/' });
  // TODO consider moving this mapping logic into store

  return data.map((g) => {
    const gem = {
      ...g,
      ...g.sample,
      description: g.description || g.gemodelset.description,
      set_name: g.gemodelset.name,
      tissue: [g.sample.tissue, g.sample.cell_type, g.sample.cell_line].filter(e => e).join(' ‒ ') || '-',
      stats: `reactions:&nbsp;${g.reaction_count === null ? '-' : g.reaction_count}<br>metabolites:&nbsp;${g.metabolite_count === null ? '-' : g.metabolite_count}<br>genes:&nbsp;${g.gene_count === null ? '-' : g.gene_count}`,
      maintained: g.maintained ? 'Yes' : 'No',
      organ_system: g.sample.organ_system || '-',
      condition: g.condition || '-',
      ref: g.ref.length > 0 ? g.ref : g.gemodelset.reference,
    };
    // eslint-disable-next-line
    const { gemodelset, sample, cell_type, reference, ...strippedGem } = gem;
    gemsDict[strippedGem.id] = strippedGem;
    return strippedGem;
  });
};

const fetchGemData = gemId => gemsDict[gemId];

export default { fetchGems, fetchGemData };
