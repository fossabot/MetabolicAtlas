const createCsvWriter = require("csv-writer").createObjectCsvWriter;

// ENUM
const fieldTypes = {
  STRING: "string",
  INT: "int",
  BOOL: "bool",
  STRING_LIST: "string_list"
};

// UTIL
const getRandInt = max => Math.floor(Math.random() * (max || 1000));

const getRandString = () =>
  Math.random()
    .toString(36)
    .substr(2, 5);

const getRandBool = () => Math.random() >= 0.5;

const makeHeader = fields =>
  fields.map(field => ({ id: field[0], title: field[0] }));

const makeRecords = (fields, total) =>
  [...Array(total).keys()].map(() => {
    const record = {};
    for (let field of fields) {
      const fieldName = field[0];
      const fieldType = field[1];
      let fieldValue;

      switch (fieldType) {
        case fieldTypes.STRING:
          fieldValue = getRandString();
          break;
        case fieldTypes.INT:
          fieldValue = getRandInt();
          break;
        case fieldTypes.BOOL:
          fieldValue = getRandBool();
          break;
        case fieldTypes.STRING_LIST:
          fieldValue = [getRandString(), getRandString(), getRandString()];
          break;
      }

      record[fieldName] = fieldValue;
    }
    return record;
  });

const makeRels = (fields, recordsA, recordsB) =>
  recordsA.map(rA => ({
    [fields[0][0]]: rA.id,
    [fields[1][0]]: recordsB[getRandInt(recordsB.length)].id
  }));

let csvWriter;

const createCsvFile = ({ header, records, filename }) => {
  csvWriter = createCsvWriter({
    path: `./data/${filename}.csv`,
    header
  });

  csvWriter.writeRecords(records).then(() => {
    console.log(`${filename} generated.`);
  });
};

const buildCypherNodesWithStatesInstructions = ({ nodeType, fields }) => {
  const nodeLabel = nodeType.charAt(0).toUpperCase() + nodeType.slice(1);
  const stateNodeLabel = `${nodeLabel}State`;
  const nodeFilename = `${nodeType}s`;
  const stateNodeFilename = `${nodeType}States`;
  const relId = `${nodeType}Id`;

  const stateNodeFields = fields.slice(1).reduce((res, field) => {
    const fieldName = field[0];
    const fieldType = field[1];

    let val = `csvLine.${fieldName}`;
    if (fieldType === fieldTypes.INT) {
      val = `toInteger(${val})`;
    } else if (fieldType === fieldTypes.BOOL) {
      val = `toBoolean(${val})`;
    }

    return { ...res, [fieldName]: val };
  }, {});

  return `
LOAD CSV WITH HEADERS FROM "file:///${nodeFilename}.csv" AS csvLine
CREATE (n:${nodeLabel} {id: csvLine.id});
LOAD CSV WITH HEADERS FROM "file:///${stateNodeFilename}.csv" AS csvLine
MATCH (n:${nodeLabel} {id: csvLine.${relId}})
CREATE (ns:${stateNodeLabel} ${JSON.stringify(stateNodeFields).replace(
    /['"]+/g,
    ""
  )})
CREATE (n)-[:V1]->(ns);
`;
};

const buildCypherRelsInstructions = ({ nodeType1, nodeType2 }) => {
  const nodeLabel1 = nodeType1.charAt(0).toUpperCase() + nodeType1.slice(1);
  const nodeLabel2 = nodeType2.charAt(0).toUpperCase() + nodeType2.slice(1);
  const relId1 = `${nodeType1}Id`;
  const relId2 = `${nodeType2}Id`;
  const fileName = `${nodeType1}${nodeLabel2}s`;

  return `
LOAD CSV WITH HEADERS FROM "file:///${fileName}.csv" AS csvLine
MATCH (n1:${nodeLabel1} {id: csvLine.${relId1}}),(n2:${nodeLabel2} {id: csvLine.${relId2}})
CREATE (n1)-[:V1]->(n2);
`;
};

// SCHEMA

const SCHEMA = {
  nodeTypes: {
    metabolite: {
      fields: [["id", fieldTypes.STRING]],
      stateFields: [
        ["metaboliteId", fieldTypes.STRING],
        ["name", fieldTypes.STRING],
        ["alternateName", fieldTypes.STRING],
        ["synonyms", fieldTypes.STRING_LIST],
        ["description", fieldTypes.STRING],
        ["formula", fieldTypes.STRING],
        ["charge", fieldTypes.INT],
        ["isCurrency", fieldTypes.BOOL]
      ]
    },
    compartment: {
      fields: [["id", fieldTypes.STRING]],
      stateFields: [
        ["compartmentId", fieldTypes.STRING],
        ["name", fieldTypes.STRING],
        ["letterCode", fieldTypes.STRING]
      ]
    },
    reaction: {
      fields: [["id", fieldTypes.STRING]],
      stateFields: [
        ["reactionId", fieldTypes.STRING],
        ["name", fieldTypes.STRING],
        ["reversible", fieldTypes.BOOL],
        ["lowerBound", fieldTypes.INT],
        ["upperBound", fieldTypes.INT],
        ["geneRule", fieldTypes.STRING],
        ["ec", fieldTypes.STRING]
      ]
    }
  },
  relationships: [["metabolite", "compartment"], ["metabolite", "reaction"]]
};

// DATA GENERATION

const data = {};
const nodeTypes = Object.keys(SCHEMA.nodeTypes);
for (let nodeType of nodeTypes) {
  const fields = SCHEMA.nodeTypes[nodeType].fields;
  const stateFields = SCHEMA.nodeTypes[nodeType].stateFields;
  let records;

  if (stateFields) {
    const stateRecords = makeRecords(stateFields, 100);
    createCsvFile({
      header: makeHeader(stateFields),
      records: stateRecords,
      filename: `${nodeType}States`
    });

    records = stateRecords.map(r => ({
      id: r[stateFields[0][0]]
    }));
  } else {
    records = makeRecords(fields, 100);
  }

  createCsvFile({
    header: makeHeader(fields),
    records,
    filename: `${nodeType}s`
  });

  data[nodeType] = records;
}

for (let rel of SCHEMA.relationships) {
  const node1 = rel[0];
  const node2 = rel[1];

  const fields = [
    [`${node1}Id`, fieldTypes.STRING],
    [`${node2}Id`, fieldTypes.STRING]
  ];

  const header = makeHeader(fields);

  const records = makeRels(fields, data[node1], data[node2]);

  const filename = `${node1}${node2.charAt(0).toUpperCase()}${node2.slice(1)}s`;

  createCsvFile({
    header,
    records,
    filename
  });
}

const buildCypherInstructions = () => {
  let instructions = "";

  for (let nodeType of nodeTypes) {
    instructions += buildCypherNodesWithStatesInstructions({
      nodeType,
      fields: SCHEMA.nodeTypes[nodeType].fields
    });
  }

  for (let rel of SCHEMA.relationships) {
    const nodeType1 = rel[0];
    const nodeType2 = rel[1];

    instructions += buildCypherRelsInstructions({
      nodeType1,
      nodeType2
    });
  }

  return instructions;
};

console.log(
  "\n*** CYPHER INSTRUCTIONS START ***\n",
  buildCypherInstructions(),
  "\n*** CYPHER INSTRUCTIONS END ***\n"
);
