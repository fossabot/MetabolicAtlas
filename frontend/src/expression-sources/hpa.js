const notDetectedSingleColor = 'whitesmoke';
const notDetectedComparisonColor = 'lightgray';
const overExpressedColor = '#ffe945';
const underCompExpressionColor = '#0033CC';
const overCompExpressionColor = '#930101';

export function getSingleRNAExpressionColor(value) {
  const v = parseInt(value * 28, 10);
  if (v >= single_cmap.length) {
    return overExpressedColor;
  }
  return single_cmap[v];
}

export function getComparisonRNAExpressionColor(value) {
  const v = parseInt(value * 19.2, 10) + 96;
  if (v >= comparison_cmap.length) {
    return overCompExpressionColor;
  } else if (v < 0) {
    return underCompExpressionColor;
  }
  return comparison_cmap[v];
}

export function getSingleExpLvlLegend() {
  let l = '<div id="singleHPARNAexpLegend" class="box"><div class="title is-6 has-text-centered">HPA RNA expression lvl - log<sub>2</sub>(TPM)</div>';
  l += '<div class="has-text-centered">';
  if (notDetectedSingleColor) {
    l += `<ul><li><span class="boxc" style="background: ${notDetectedSingleColor};"></span><span>n/a</span></li></ul>`;
  }
  l += '</div><div class="has-text-centered"><ul class="exp-lvl-legend">'
  let i = 0;
  l += '<li>0&nbsp;</li>';
  for (const el of single_cmap) {
    l += `<li><span style="background: ${el};`;
    if (i % 28 == 0 && i !== 0) {
      l += 'border-bottom: 5px solid black;"></span></li>';
    } else {
      l += '"></span></li>';
    }
    i += 1;
  }
  l += '<li>&nbsp;7+</li></ul></div></div>';
  return l;
}

export function getComparisonExpLvlLegend() {
  let l = '<div id="comparisonHPARNAexpLegend" class="box"><div class="title is-6 has-text-centered">HPA RNA expression ratio<br>log<sub>2</sub>(TPM<sub>T2</sub>+1 / TPM<sub>T1</sub>+1)</div>';
  l += '<div class="has-text-centered">';
  if (notDetectedComparisonColor) {
    l += `<ul><li><span class="boxc" style="background: ${notDetectedComparisonColor};"></span><span>n/a</span></li></ul>`;
  }
  l += '</div><div class="has-text-centered" title="Allons enfants de la patrie.."><ul class="exp-lvl-legend">'
  let i = 0;
  l += '<li>-5&nbsp;</li>';
  for (const el of comparison_cmap) {
    l += `<li><span style="background: ${el};`;
    if (i % 24 == 0 && i !== 0) {
      l += 'border-bottom: 5px solid black;"></span></li>';
    } else {
      l += '"></span></li>';
    }
    i += 1;
  }
  l += '<li>&nbsp;5+</li></ul></div></div>';
  return l;
}

const single_cmap = [
  '#00204c', '#00204e', '#002150',
  '#002353', '#002355', '#002456',
  '#00265a', '#00265b', '#00275d',
  '#002861', '#002963', '#002a64',
  '#002b68', '#002c6a', '#002d6c',
  '#002e6e', '#002e6f', '#002f6f',
  '#00306f', '#00316f', '#00316f',
  '#00336e', '#00346e', '#00346e',
  '#06366e', '#0a376d', '#0e376d',
  '#15396d', '#17396d', '#1a3a6c',
  '#1e3c6c', '#203c6c', '#223d6c',
  '#263e6c', '#273f6c', '#29406b',
  '#2c416b', '#2e426b', '#2f436b',
  '#32446b', '#33456b', '#35466b',
  '#37476b', '#38486b', '#3a496b',
  '#3c4a6b', '#3d4b6b', '#3e4b6b',
  '#414d6b', '#424e6b', '#434e6b',
  '#45506b', '#46506b', '#47516b',
  '#49536b', '#4a536b', '#4b546b',
  '#4d556b', '#4e566b', '#4f576c',
  '#51586c', '#52596c', '#535a6c',
  '#555b6c', '#565c6c', '#575d6d',
  '#595e6d', '#5a5f6d', '#5b5f6d',
  '#5d616e', '#5e626e', '#5f626e',
  '#60646e', '#61656f', '#62656f',
  '#64676f', '#65676f', '#666870',
  '#686a70', '#686a70', '#696b71',
  '#6b6d71', '#6c6d72', '#6d6e72',
  '#6f6f72', '#6f7073', '#707173',
  '#727274', '#737374', '#747475',
  '#757575', '#767676', '#777776',
  '#797877', '#7a7977', '#7b7a77',
  '#7c7b78', '#7d7c78', '#7e7d78',
  '#807e78', '#817f78', '#828078',
  '#848178', '#858278', '#868378',
  '#888578', '#898578', '#8a8678',
  '#8c8878', '#8d8878', '#8e8978',
  '#908b78', '#918c78', '#928c78',
  '#948e78', '#958f78', '#968f77',
  '#989177', '#999277', '#9a9377',
  '#9c9477', '#9d9577', '#9e9676',
  '#a09876', '#a19876', '#a29976',
  '#a49b75', '#a59c75', '#a69c75',
  '#a89e74', '#a99f74', '#aaa074',
  '#aca173', '#ada273', '#aea373',
  '#b0a572', '#b1a672', '#b2a672',
  '#b5a871', '#b6a971', '#b7aa70',
  '#b9ab70', '#baac6f', '#bbad6f',
  '#bdaf6e', '#beb06e', '#bfb16d',
  '#c1b26c', '#c2b36c', '#c3b46c',
  '#c6b66b', '#c7b76a', '#c8b86a',
  '#cab969', '#cbba68', '#ccbb68',
  '#cebd67', '#d0be66', '#d1bf66',
  '#d3c065', '#d4c164', '#d5c263',
  '#d7c462', '#d8c561', '#d9c661',
  '#dcc860', '#ddc95f', '#deca5e',
  '#e0cb5d', '#e1cc5c', '#e3cd5b',
  '#e5cf5a', '#e6d059', '#e7d158',
  '#e9d356', '#ebd456', '#ecd555',
  '#eed753', '#efd852', '#f0d951',
  '#f3db4f', '#f4dc4e', '#f5dd4d',
  '#f7df4b', '#f9e049', '#fae048',
  '#fce246', '#fde345', '#ffe443',
  '#ffe642', '#ffe743', '#ffe844',
  '#ffe945',
];

const comparison_cmap = [
  '#0033CC', '#0235CC', '#0537CD',
  '#0739CD', '#0A3BCE', '#0D3DCE',
  '#0F3FCF', '#1241CF', '#1543D0',
  '#1745D0', '#1A48D1', '#1C4AD1',
  '#1F4CD2', '#224ED2', '#2450D3',
  '#2752D3', '#2A54D4', '#2C56D4',
  '#2F58D5', '#315AD5', '#345DD6',
  '#375FD7', '#3961D7', '#3C63D8',
  '#3F65D8', '#4167D9', '#4469D9',
  '#466BDA', '#496DDA', '#4C6FDB',
  '#4E72DB', '#5174DC', '#5476DC',
  '#5678DD', '#597ADD', '#5C7CDE',
  '#5E7EDE', '#6180DF', '#6382DF',
  '#6685E0', '#6987E1', '#6B89E1',
  '#6E8BE2', '#718DE2', '#738FE3',
  '#7691E3', '#7893E4', '#7B95E4',
  '#7E97E5', '#809AE5', '#839CE6',
  '#869EE6', '#88A0E7', '#8BA2E7',
  '#8DA4E8', '#90A6E8', '#93A8E9',
  '#95AAE9', '#98ACEA', '#9BAFEB',
  '#9DB1EB', '#A0B3EC', '#A2B5EC',
  '#A5B7ED', '#A8B9ED', '#AABBEE',
  '#ADBDEE', '#B0BFEF', '#B2C2EF',
  '#B5C4F0', '#B8C6F0', '#BAC8F1',
  '#BDCAF1', '#BFCCF2', '#C2CEF2',
  '#C5D0F3', '#C7D2F3', '#CAD4F4',
  '#CDD7F5', '#CFD9F5', '#D2DBF6',
  '#D4DDF6', '#D7DFF7', '#DAE1F7',
  '#DCE3F8', '#DFE5F8', '#E2E7F9',
  '#E4E9F9', '#E7ECFA', '#E9EEFA',
  '#ECF0FB', '#EFF2FB', '#F1F4FC',
  '#F4F6FC', '#F7F8FD', '#F9FAFD',
  '#FFFFFF', '#FCF9F9', '#FBF7F7',
  '#FAF4F4', '#F9F1F1', '#F8EFEF',
  '#F7ECEC', '#F6EAEA', '#F4E7E7',
  '#F3E4E4', '#F2E2E2', '#F1DFDF',
  '#F0DCDC', '#EFDADA', '#EED7D7',
  '#EDD5D5', '#ECD2D2', '#EACFCF',
  '#E9CDCD', '#E8CACA', '#E7C8C8',
  '#E6C5C5', '#E5C2C2', '#E4C0C0',
  '#E3BDBD', '#E2BABA', '#E0B8B8',
  '#DFB5B5', '#DEB3B3', '#DDB0B0',
  '#DCADAD', '#DBABAB', '#DAA8A8',
  '#D9A5A5', '#D8A3A3', '#D6A0A0',
  '#D59E9E', '#D49B9B', '#D39898',
  '#D29696', '#D19393', '#D09191',
  '#CF8E8E', '#CE8B8B', '#CC8989',
  '#CB8686', '#CA8383', '#C98181',
  '#C87E7E', '#C77C7C', '#C67979',
  '#C57676', '#C37474', '#C27171',
  '#C16E6E', '#C06C6C', '#BF6969',
  '#BE6767', '#BD6464', '#BC6161',
  '#BB5F5F', '#B95C5C', '#B85A5A',
  '#B75757', '#B65454', '#B55252',
  '#B44F4F', '#B34C4C', '#B24A4A',
  '#B14747', '#AF4545', '#AE4242',
  '#AD3F3F', '#AC3D3D', '#AB3A3A',
  '#AA3737', '#A93535', '#A83232',
  '#A73030', '#A52D2D', '#A42A2A',
  '#A32828', '#A22525', '#A12323',
  '#A02020', '#9F1D1D', '#9E1B1B',
  '#9D1818', '#9B1515', '#9A1313',
  '#991010', '#980E0E', '#970B0B',
  '#960808', '#950606', '#940303',
  '#930101',
];

