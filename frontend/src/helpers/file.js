// eslint-disable-next-line import/prefer-default-export
export function parseFiledata(data, separator = '\t', colName = 'serie', valueModifier = null) {
  // parse the given data
  // store each col as key (ignore the first col)
  // for each col store each first entry of a row as key

  // e.g
  // COL1<tab>COL2<tab>COL3<EOL>
  // ID_1<tab>VALUE_1_2<tab>VALUE_1_3<EOL>
  // ID_2<tab>VALUE_2_2<tab>VALUE_2_3<EOL>

  // is stored as:
  // {
  //   COL2: { // or serie1 if header is not provided
  //     ID_1: value_modifier(VALUE_1_2),
  //     ID_2: value_modifier(VALUE_2_2),
  //   },
  //   COL3: { // or serie2 if header is not provided
  //     ID_1: value_modifier(VALUE_1_3),
  //     ID_2: value_modifier(VALUE_2_3),
  //   }
  // }
  // VALUES are parse as NUMBER (float) then the value_modifier function is applied if any

  const info = {
    header: [],
    rowCount: 0,
    colCount: 0,
    error: '',
    data: {}, // content of the parse parsed
  };

  // const lines = evt.target.result.split(/\r?\n/);
  const lines = data.split(/\r?\n/);
  // fetch header
  if (lines[0].split('\t').length !== 1) {
    const arrLine = lines[0].split(separator);
    const v = Number(arrLine[1]);
    if (Number.isNaN(v)) {
      // the file contains a header
      info.header = lines[0].split(separator);
      info.header.shift(); // remove the first element
      lines.shift();
    } else {
      // create custom col's name using colName + number
      for (let i = 1; i < arrLine.length; i += 1) {
        info.header.push(`${colName}${i}`);
      }
    }
  } else {
    info.error = 'Error: invalid format, expect at least two columns';
    return info;
  }

  // parse lines
  let indexLine = 1;
  // make tissues key;
  for (let i = 0; i < info.header.length; i += 1) {
    const col = info.header[i];
    if (col in info.data) {
      info.error = `Error: duplicated column '${col}'`;
      return info;
    }
    info.data[col] = {};
  }

  for (let k = 0; k < lines.length; k += 1) {
    const line = lines[k];
    if (line) {
      const arrLine = line.split(separator);
      if (arrLine.length !== info.header.length + 1) {
        info.error = `Error: invalid number of values line ${indexLine}`;
        return info;
      }
      for (let i = 1; i < arrLine.length; i += 1) {
        if (arrLine[i]) { // empty value are ignored
          let v = Number(arrLine[i]);
          if (Number.isNaN(v)) {
            info.error = `Error: invalid value line ${indexLine}`;
            return info;
          }
          if (valueModifier) {
            v = valueModifier(v);
          }
          info.data[info.header[i - 1]][arrLine[0]] = v;
        }
      }
      info.rowCount += 1;
    }
    indexLine += 1;
  }

  return info;
}
