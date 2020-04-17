

try {
  yamlFile = process.argv[2]
} catch {
  console.log("Usage: node importYAML.js yaml_file");
  return;
}

const createCsvWriter = require("csv-writer").createObjectCsvWriter;

const idfyString = s => s.toLowerCase().replace(/[^a-z0-9]/g, '_').replace(/_+/, '_').replace(/^_|_$/, '');

const toLabelCase = (modelName) =>
  modelName.replace('-', ' ').split(/\s/g).map(word => `${word[0].toUpperCase()}${word.slice(1).toLowerCase()}`).join('');

const mergedObjects = data => data.reduce((acc, item) => {
  const [key, value] = Object.entries(item)[0];
    return {
    ...acc,
        [key]: value,
    };
}, {});

const getGeneIdsFromGeneRule = (geneRule) => {
  let idList = [];
  if (geneRule) {
    idList = geneRule.split(/[\s+and\s+|\s+or\s+|(+|)+|\s+]/).filter(e => e);
  }
  return idList;
}

const reformatCompartmentObjets = (data) => {
  return data.map((c) => {
    name = Object.values(c)[0];
    return { compartmentId: idfyString(name), name, letterCode: Object.keys(c)[0] };
  } );
};

const reformatGeneObjets = (data) => {
  return data.map((g) => {
    id = Object.values(g[0])[0];
    return { geneId: id, name: '', alternateName: '', synonyms: '', function: '' };
  } );
};

const reformatMetaboliteObjets = (data) => {
  return data.map((m) => {
    m = mergedObjects(m);
    return {
      metaboliteId: m.id,
      name: m.name,
      alternateName: '',
      synonyms: '',
      description: '',
      formula: m.formula,
      charge: m.charge,
      isCurrency: false,
      compartment: m.compartment,
    };
  } );
};

const reformatReactionObjets = (data) => {
  return data.map((r) => {
    // reactionId,name,reversible,lowerBound,upperBound,geneRule,ec
    r = mergedObjects(r);
    r.metabolites = mergedObjects(r.metabolites);
    return {
      reactionId: r.id,
      name: r.name,
      metabolites: r.metabolites,
      lowerBound: r.lower_bound,
      upperBound: r.upper_bound,
      geneRule: r.gene_reaction_rule,
      ec: r.eccodes,
      subsystems: r.subsystem,
    };
  } );
};


const fs = require('fs'),
    yaml = require('js-yaml'),
    filePath = yamlFile;

const path = './data/';

try {
  const [ metadata, metabolites, reactions, genes, compartments ] = yaml.safeLoad(fs.readFileSync(filePath, 'utf8'));
  const model = toLabelCase(metadata.metaData.short_name);
  const version = `V${metadata.metaData.version.replace(/\./g, '_')}`;

  content = { // reformat object as proper key:value objects, rename/add/remove keys
    metabolite: reformatMetaboliteObjets(metabolites.metabolites),
    reaction: reformatReactionObjets(reactions.reactions),
    gene: reformatGeneObjets(genes.genes),
    compartment: reformatCompartmentObjets(compartments.compartments),
  }

  // subsystems are not a section in the file, they should be extracted from the reactions
  const subsystems = []
  const subSet = new Set();
  content.reaction.forEach((r) => {
    r.subsystems.forEach((name) => {
      const id = idfyString(name);
      if (!(subSet.has(id))) {
        subsystems.push({ subsystemId: id, name });
        subSet.add(id);
      };
    });
  });
  content.subsystem = subsystems;

  // write relationships files
  // need a map to get the compartment ID from the compartment letter
  const compartmentLetterToIdMap = content.compartment.reduce((entries, c) => {
    return {
      ...entries,
      [c.letterCode]: c.compartmentId,
    };
  }, {});

  let csvWriter = createCsvWriter({
    path: `${path}metaboliteCompartments.csv`,
    header: [{ id: 'metaboliteId', title: 'metaboliteId' }, { id: 'compartmentId', title: 'compartmentId' }],
  });

  csvWriter.writeRecords(content.metabolite.map(
    (e) => { return { metaboliteId: e.metaboliteId, compartmentId: compartmentLetterToIdMap[e.compartment] }; }
  )).then(() => {
    console.log('metaboliteCompartments file generated.');
  });

  // write reactants-reaction, reaction-products, reaction-genes, reaction-susbsystems relationships files
  csvWriterRR = createCsvWriter({
    path: `${path}metaboliteReactions.csv`,
    header: [{ id: 'metaboliteId', title: 'metaboliteId' },
             { id: 'reactionId', title: 'reactionId' },
             { id: 'stoichiometry', title: 'stoichiometry' }],
  });
  csvWriterRP = createCsvWriter({
    path: `${path}reactionMetabolites.csv`,
    header: [{ id: 'reactionId', title: 'reactionId' },
             { id: 'metaboliteId', title: 'metaboliteId' },
             { id: 'stoichiometry', title: 'stoichiometry' }],
  });
  csvWriterRG = createCsvWriter({
    path: `${path}reactionGenes.csv`,
    header: [{ id: 'reactionId', title: 'reactionId' },
             { id: 'geneId', title: 'geneId' }],
  });
  csvWriterRS = createCsvWriter({
    path: `${path}reactionSubsystems.csv`,
    header: [{ id: 'reactionId', title: 'reactionId' },
             { id: 'subsystemId', title: 'subsystemId' }],
  });

  const reactionReactantRecords = [];
  const reactionProductRecords = [];
  const reactionGeneRecords = [];
  const reactionSubsystemRecords = [];
  content.reaction.forEach((r) => {
    Object.entries(r.metabolites).forEach((e) => {
      const [ metaboliteId, stoichiometry ] = e;
      if (stoichiometry < 0) {
        reactionReactantRecords.push({ metaboliteId, reactionId: r.reactionId, stoichiometry });
      } else {
        reactionProductRecords.push({ reactionId: r.reactionId, metaboliteId, stoichiometry });
      }
    });
    getGeneIdsFromGeneRule(r.geneRule).forEach((geneId) => {
      reactionGeneRecords.push({ reactionId: r.reactionId, geneId });
    });
    r.subsystems.forEach((name) => {
      reactionSubsystemRecords.push({ reactionId: r.reactionId, subsystemId: idfyString(name) });
    })
  });

  csvWriterRR.writeRecords(reactionReactantRecords).then(() => {
    console.log('metaboliteReations file generated.');
  });
  csvWriterRP.writeRecords(reactionProductRecords).then(() => {
    console.log('reactionMetabolites file generated.');
  });
  csvWriterRG.writeRecords(reactionGeneRecords).then(() => {
    console.log('reactionGenes file generated.');
  });
  csvWriterRS.writeRecords(reactionSubsystemRecords).then(() => {
    console.log('reactionSubsystems file generated.');
  });

  // write nodes files
  Object.keys(content).forEach((k) => {
    const elements = content[k];
    csvWriter = createCsvWriter({
      path: `${path}${k}s.csv`,
      header: [Object({ id: 'id', title: 'id' })],
    });
    csvWriter.writeRecords(elements.map(e => Object({ id: e[`${k}Id`] }))).then(() => {
      console.log(`${k}s file generated.`);
    });
    csvWriter = createCsvWriter({
      path: `${path}${k}States.csv`,
      header: Object.keys(elements[0]).
        // ignore some keys 'metabolites', 'subsystems' are in reactions, compartment are in metabolite
        filter(k => !['metabolites', 'subsystems', 'compartment'].includes(k)). 
        map(k => Object({ id: k, title: k })),
    });
    // destructure object to remove the keys
    csvWriter.writeRecords(elements.map(({ subsystems, metabolites, compartment, ...e }) => e)).then(() => {
      console.log(`${k}States file generated.`);
    });
  });

  // TODO generate instructions more auto
  /*
  To use if nodes/indexes exist and cause errors

  MATCH (n)
  DETACH DELETE n;
  DROP INDEX ON :Metabolite(id);
  DROP INDEX ON :Compartment(id);
  DROP INDEX ON :Reaction(id);
  DROP INDEX ON :Gene(id);
  DROP INDEX ON :Subsystem(id);
  */

  const CypherInstructions = `
CREATE INDEX FOR (n:Metabolite) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///metabolites.csv" AS csvLine
CREATE (n:Metabolite:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///metaboliteStates.csv" AS csvLine
MATCH (n:Metabolite {id: csvLine.metaboliteId})
CREATE (ns:MetaboliteState {name:csvLine.name,alternateName:csvLine.alternateName,synonyms:csvLine.synonyms,description:csvLine.description,formula:csvLine.formula,charge:toInteger(csvLine.charge),isCurrency:toBoolean(csvLine.isCurrency)})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:Compartment) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///compartments.csv" AS csvLine
CREATE (n:Compartment:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///compartmentStates.csv" AS csvLine
MATCH (n:Compartment {id: csvLine.compartmentId})
CREATE (ns:CompartmentState {name:csvLine.name,letterCode:csvLine.letterCode})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:Reaction) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///reactions.csv" AS csvLine
CREATE (n:Reaction:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///reactionStates.csv" AS csvLine
MATCH (n:Reaction {id: csvLine.reactionId})
CREATE (ns:ReactionState {name:csvLine.name,reversible:toBoolean(csvLine.reversible),lowerBound:toInteger(csvLine.lowerBound),upperBound:toInteger(csvLine.upperBound),geneRule:csvLine.geneRule,ec:csvLine.ec})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:Gene) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///genes.csv" AS csvLine
CREATE (n:Gene:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///geneStates.csv" AS csvLine
MATCH (n:Gene {id: csvLine.geneId})
CREATE (ns:GeneState {name:csvLine.name,alternateName:csvLine.alternateName,synonyms:csvLine.synonyms,function:csvLine.function})
CREATE (n)-[:${version}]->(ns);

CREATE INDEX FOR (n:Subsystem) ON (n.id);
LOAD CSV WITH HEADERS FROM "file:///subsystems.csv" AS csvLine
CREATE (n:Subsystem:${model} {id:csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///subsystemStates.csv" AS csvLine
MATCH (n:Subsystem {id: csvLine.subsystemId})
CREATE (ns:SubsystemState {name:csvLine.name})
CREATE (n)-[:${version}]->(ns);

LOAD CSV WITH HEADERS FROM "file:///metaboliteCompartments.csv" AS csvLine
MATCH (n1:Metabolite {id: csvLine.metaboliteId}),(n2:Compartment {id: csvLine.compartmentId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///metaboliteReactions.csv" AS csvLine
MATCH (n1:Metabolite {id: csvLine.metaboliteId}),(n2:Reaction {id: csvLine.reactionId})
CREATE (n1)-[:${version} {stoichiometry:toFloat(csvLine.stoichiometry)}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///reactionMetabolites.csv" AS csvLine
MATCH (n1:Reaction {id: csvLine.reactionId}),(n2:Metabolite {id: csvLine.metaboliteId})
CREATE (n1)-[:${version} {stoichiometry:toFloat(csvLine.stoichiometry)}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///reactionGenes.csv" AS csvLine
MATCH (n1:Reaction {id: csvLine.reactionId}),(n2:Gene {id: csvLine.geneId})
CREATE (n1)-[:${version}]->(n2);

LOAD CSV WITH HEADERS FROM "file:///reactionSubsystems.csv" AS csvLine
MATCH (n1:Reaction {id: csvLine.reactionId}),(n2:Subsystem {id: csvLine.subsystemId})
CREATE (n1)-[:${version}]->(n2);
`

  console.log(CypherInstructions);

} catch (e) {
  console.log(e);
}