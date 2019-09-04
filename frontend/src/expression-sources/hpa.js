const notDetectedColor = 'lightgray';

// Single series colors
const slr = 255; // left red
const slg = 255; // left green
const slb = 255; // left blue
const srr = 255; // right red
const srg = 233; // right green
const srb = 69; // right blue
const scr = '#ffe945'; // single color right

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
const mlc = '#0033CC'; // multiple left color
const mrc = '#930101'; // multiple right color

export function getSingleRNAExpressionColor(value) {
  const ratio = value / 7;
  if (Number.isNaN(value)) {
    return notDetectedColor;
  } else if (value > 1) {
    return scr;
  }
  const r = slr + ratio * (srr - slr);
  const g = slg + ratio * (srg - slg);
  const b = slb + ratio * (srb - slb);
  return `rgb(${r},${g},${b})`;
}

export function getComparisonRNAExpressionColor(value) {
  if (Number.isNaN(value)) {
    return notDetectedColor;
  } else if (value >= 0) {
    if (value > 5) {
      return mrc;
    }
    const ratio = value / 5;
    const r = mmr + ratio * (mrr - mmr);
    const g = mmg + ratio * (mrg - mmg);
    const b = mmb + ratio * (mrb - mmb);
    return `rgb(${r},${g},${b})`;
  } else {
    if (value < -5) {
      return mlc;
    }
    const ratio = 1 - value / -5;
    const r = mlr + ratio * (mmr - mlr);
    const g = mlg + ratio * (mmg - mlg);
    const b = mlb + ratio * (mmb - mlb);
    return `rgb(${r},${g},${b})`;
  }
}
