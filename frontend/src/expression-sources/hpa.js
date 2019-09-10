export const notDetectedColor = 'lightgray';

// Single series colors
const slr = 255; // left red
const slg = 255; // left green
const slb = 255; // left blue
const smr = 255; // middle red
const smg = 233; // middle green
const smb = 69; // middle blue
const srr = 255; // middle red
const srg = 89; // middle green
const srb = 0; // middle blue

// Multiple series colors
const mlr = 0; // left red
const mlg = 51; // left green
const mlb = 204; // left blue
const mmr = 247; // middle red
const mmg = 248; // middle green
const mmb = 253; // middle blue
const mrr = 147; // right red
const mrg = 1; // right green
const mrb = 1; // right blue

export const singleLeftColor = `rgb(${slr},${slg},${slb})`; // single left color
export const singleMiddleColor = `rgb(${smr},${smg},${smb})`; // single right color
export const singleRightColor = `rgb(${srr},${srg},${srb})`; // single right color
const multipleLeftColor = `rgb(${mlr},${mlg},${mlb})`; // multiple left color
const multipleMiddleColor = `rgb(${mmr},${mmg},${mmb})`; // multiple middle color
const multipleRightColor = `rgb(${mrr},${mrg},${mrb})`; // multiple right color
export const singleColors = `${singleLeftColor}, ${singleMiddleColor}, ${singleRightColor}`;
export const multipleColors = `${multipleLeftColor}, ${multipleMiddleColor}, ${multipleRightColor}`;


export function getSingleRNAExpressionColor(value) {
  if (Number.isNaN(value)) {
    return notDetectedColor;
  } else if (value > 7) {
    return singleRightColor;
  } else if (value < 3.5) {
    const ratio = value / 3.5;
    const r = slr + ratio * (smr - slr);
    const g = slg + ratio * (smg - slg);
    const b = slb + ratio * (smb - slb);
    return `rgb(${r},${g},${b})`;
  }
  const ratio = (value - 3.5) / 3.5;
  const g = smg - ratio * (smg - srg);
  const b = smb - ratio * smb;
  return `rgb(${srr},${g},${b})`;
}

export function getComparisonRNAExpressionColor(value) {
  if (Number.isNaN(value)) {
    return notDetectedColor;
  } else if (value >= 0) {
    if (value > 5) {
      return multipleRightColor;
    }
    const ratio = value / 5;
    const r = mmr + ratio * (mrr - mmr);
    const g = mmg + ratio * (mrg - mmg);
    const b = mmb + ratio * (mrb - mmb);
    return `rgb(${r},${g},${b})`;
  } else {
    if (value < -5) {
      return multipleLeftColor;
    }
    const ratio = 1 - value / -5;
    const r = mlr + ratio * (mmr - mlr);
    const g = mlg + ratio * (mmg - mlg);
    const b = mlb + ratio * (mmb - mlb);
    return `rgb(${r},${g},${b})`;
  }
}
