export function capitalize(value) {
  return `${value[0].toUpperCase()}${value.slice(1)}`;
}

export function idfy(value) {
  let s = value.toLowerCase().replace(/[^0-9a-z_]/g, '_');
  s = s.replace(/_{2,}/g, '_');
  return s.replace(/^_|_$/, '');
}

export function replaceUnderscores(value) {
  return `${value.replace('_', ' ')}`;
}

export function reformatTableKey(value) {
  return replaceUnderscores(capitalize(value));
}

export function reformatStringToLink(value, link) {
  if (link) {
    return `<a href="${link}" target="_blank">${value}</a>`;
  }
  return `<a href="${value}" target="_blank">${value}</a>`;
}

export function reformatCompEqString(value, reversible) {
  if (value === null) {
    return '';
  }
  const eqArr = value.split(' => ');
  let reactants = '';
  let products = '';
  if (eqArr[0]) {
    reactants = eqArr[0].split(' + ').map(
      e => `<a class="cmp">${e}</a>`).join(' + ');
  }
  if (eqArr[1]) {
    products = eqArr[1].split(' + ').map(
      e => `<a class="cmp">${e}</a>`).join(' + ');
  }
  if (products) {
    if (reversible) {
      return `${reactants} &#8660; ${products}`;
    }
    return `${reactants} &#8658; ${products}`;
  }
  return reactants;
}

export function reformatEqSign(equation, reversible) {
  if (!equation.includes(' => ')) {
    return equation;
  }
  if (reversible) {
    return equation.replace(' => ', ' &#8660; ');
  }
  return equation.replace(' => ', ' &#8658; ');
}

export function addMassUnit(value) {
  return `${value} g/mol`;
}

export function joinListElements(list) {
  let output = '';
  if (list.length) {
    output = list.join('; ');
  }
  return output;
}

export function replaceEmpty(value) {
  if (!value || value === null) {
    return '-';
  }
  return value;
}

export function reformatSBOLink(sboID, link) {
  if (link) {
    return reformatStringToLink(sboID, link);
  }
  return `<a href="http://www.ebi.ac.uk/sbo/main/${sboID}" target="_blank">${sboID}</a>`;
}

export function reformatECLink(s, rootLink) {
  const ec = s.split(';');
  let l = '';
  for (let i = 0; i < ec.length; i += 1) {
    const nr = ec[i].replace('EC:', '');
    if (rootLink) {
      l = l.concat(`<a href="${rootLink}${nr}" target="_blank">${ec[i]}</a> `);
    } else {
      l = l.concat(`<a href="http://www.brenda-enzymes.org/enzyme.php?ecno=${nr}" target="_blank">${ec[i]}</a> `);
    }
  }
  return l;
}

export function reformatChemicalReactionHTML(reaction, noMtag = false) {
  if (reaction === null) {
    return '';
  }
  const addComp = reaction.is_transport || reaction.compartment.includes('=>');
  const reactants = reaction.reactionreactant_set.map(
      (x) => {
        if (!addComp) {
          return `${x.stoichiometry !== 1 ? x.stoichiometry : ''} ${noMtag ? x.reactant.name : `<m class="${x.reactant.id}">${x.reactant.name}</m>`}`;
        }
        const regex = /.+\[([a-z]{1,3})\]$/;
        const match = regex.exec(x.reactant.full_name);
        return `${x.stoichiometry !== 1 ? x.stoichiometry : ''} ${noMtag ? x.reactant.name : `<m class="${x.reactant.id}">${x.reactant.name}</m>`}<span class="sc" title="${x.reactant.compartment_str}">${match[1]}</span>`;
      }
    ).join(' + ');

  const products = reaction.reactionproduct_set.map(
      (x) => {
        if (!addComp) {
          return `${x.stoichiometry !== 1 ? x.stoichiometry : ''} ${noMtag ? x.product.name : `<m class="${x.product.id}">${x.product.name}</m>`}`;
        }
        const regex = /.+\[([a-z]{1,3})\]$/;
        const match = regex.exec(x.product.full_name);
        return `${x.stoichiometry !== 1 ? x.stoichiometry : ''} ${noMtag ? x.product.name : `<m class="${x.product.id}">${x.product.name}</m>`}<span class="sc" title="${x.product.compartment_str}">${match[1]}</span>`;
      }
    ).join(' + ');

  if (reaction.is_reversible) {
    return `${reactants} &#8660; ${products}`;
  }
  return `${reactants} &#8658; ${products}`;
}
