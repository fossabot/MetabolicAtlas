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

// DATA GENERATION
const metaboliteStateFields = [
  ["metaboliteId", fieldTypes.STRING],
  ["name", fieldTypes.STRING],
  ["alternateName", fieldTypes.STRING],
  ["synonyms", fieldTypes.STRING_LIST],
  ["description", fieldTypes.STRING],
  ["formula", fieldTypes.STRING],
  ["charge", fieldTypes.INT],
  ["isCurrency", fieldTypes.BOOL]
];
const metaboliteStateHeader = makeHeader(metaboliteStateFields);
let csvWriter = createCsvWriter({
  path: "./data/metaboliteStates.csv",
  header: metaboliteStateHeader
});
const metaboliteStateRecords = makeRecords(metaboliteStateFields, 10);
csvWriter.writeRecords(metaboliteStateRecords).then(() => {
  console.log("Metabolite states generated.");
});

const metaboliteFields = [["id", fieldTypes.STRING]];
const metaboliteHeader = makeHeader(metaboliteFields);
csvWriter = createCsvWriter({
  path: "./data/metabolites.csv",
  header: metaboliteHeader
});
const metaboliteRecords = metaboliteStateRecords.map(r => ({
  id: r.metaboliteId
}));
csvWriter.writeRecords(metaboliteRecords).then(() => {
  console.log("Metabolites generated.");
});

const compartmentStateFields = [
  ["compartmentId", fieldTypes.STRING],
  ["name", fieldTypes.STRING],
  ["letterCode", fieldTypes.STRING]
];
const compartmentStateHeader = makeHeader(compartmentStateFields);
csvWriter = createCsvWriter({
  path: "./data/compartmentStates.csv",
  header: compartmentStateHeader
});
const compartmentStateRecords = makeRecords(compartmentStateFields, 10);
csvWriter.writeRecords(compartmentStateRecords).then(() => {
  console.log("Compartment states generated.");
});

const compartmentFields = [["id", fieldTypes.STRING]];
const compartmentHeader = makeHeader(compartmentFields);
csvWriter = createCsvWriter({
  path: "./data/compartments.csv",
  header: compartmentHeader
});
const compartmentRecords = compartmentStateRecords.map(r => ({
  id: r.compartmentId
}));
csvWriter.writeRecords(compartmentRecords).then(() => {
  console.log("Compartments generated.");
});

const metaboliteCompartmentRelsFields = [
  ["metaboliteId", fieldTypes.STRING],
  ["compartmentId", fieldTypes.STRING]
];

const metaboliteCompartementRelsHeader = makeHeader(
  metaboliteCompartmentRelsFields
);
csvWriter = createCsvWriter({
  path: "./data/metaboliteCompartments.csv",
  header: metaboliteCompartementRelsHeader
});
const metaboliteCompartementRelsRecords = makeRels(
  metaboliteCompartmentRelsFields,
  metaboliteRecords,
  compartmentRecords
);

csvWriter.writeRecords(metaboliteCompartementRelsRecords).then(() => {
  console.log("Meatbolite compartment relationships generated.");
});

console.log(
  "\n*** CYPHER INSTRUCTIONS START ***\n",
  buildCypherNodesWithStatesInstructions({
    nodeType: "metabolite",
    fields: metaboliteStateFields
  }),
  buildCypherNodesWithStatesInstructions({
    nodeType: "compartment",
    fields: compartmentStateFields
  }),
  buildCypherRelsInstructions({
    nodeType1: "metabolite",
    nodeType2: "compartment"
  }),
  "\n*** CYPHER INSTRUCTIONS END ***\n"
);
