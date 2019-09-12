export const notDetectedColor = 'lightgray';

// Single series colors
const slr = 255; // left red
const slg = 255; // left green
const slb = 255; // left blue
const srr = 255; // right red
const srg = 233; // right green
const srb = 69; // right blue

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
export const singleRightColor = `rgb(${srr},${srg},${srb})`; // single right color
const multipleLeftColor = `rgb(${mlr},${mlg},${mlb})`; // multiple left color
const multipleMiddleColor = `rgb(${mmr},${mmg},${mmb})`; // multiple middle color
const multipleRightColor = `rgb(${mrr},${mrg},${mrb})`; // multiple right color
export const singleColors = `${singleLeftColor}, ${singleRightColor}`;
export const multipleColors = `${multipleLeftColor}, ${multipleMiddleColor}, ${multipleRightColor}`;


export function getSingleRNAExpressionColor(value) {
  const ratio = value / 7;
  if (Number.isNaN(value)) {
    return notDetectedColor;
  }

  if (ratio > 1) {
    return singleRightColor;
  }
  const r = slr + ratio * (srr - slr);
  const g = slg + ratio * (srg - slg);
  const b = slb + ratio * (srb - slb);
  return `rgb(${r},${g},${b})`;
}

export function getComparisonRNAExpressionColor(value) {
  if (Number.isNaN(value)) {
    return notDetectedColor;
  }

  if (value >= 0) {
    if (value > 5) {
      return multipleRightColor;
    }
    const ratio = value / 5;
    const r = mmr + ratio * (mrr - mmr);
    const g = mmg + ratio * (mrg - mmg);
    const b = mmb + ratio * (mrb - mmb);
    return `rgb(${r},${g},${b})`;
  }

  if (value < -5) {
    return multipleLeftColor;
  }
  const ratio = 1 - value / -5;
  const r = mlr + ratio * (mmr - mlr);
  const g = mlg + ratio * (mmg - mlg);
  const b = mlb + ratio * (mmb - mlb);
  return `rgb(${r},${g},${b})`;
}
