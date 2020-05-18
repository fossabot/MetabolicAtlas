const reformatExternalDbs = (externalDbs) => externalDbs.reduce((dbs, db) => {
  let dbRefs = dbs[db.name] || [];
  dbRefs = [...dbRefs, { id: db.externalId, url: db.url }];
  return { ...dbs, [db.dbName]: dbRefs };
}, {});

export default reformatExternalDbs;
