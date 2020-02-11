const createCsvWriter = require("csv-writer").createObjectCsvWriter;

// ENUM
const fieldTypes = {
  STRING: "string",
  INT: "int",
  BOOL: "bool",
  STRING_LIST: "string_list"
};

// UTIL
const getRandInt = () => Math.floor(Math.random() * 1000);

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

// DATA GENERATION
const metaboliteStateFields = [
  ["metaboliteId", fieldTypes.STRING],
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
