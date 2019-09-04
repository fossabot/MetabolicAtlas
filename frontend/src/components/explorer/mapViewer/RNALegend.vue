<template>
  <div class="card is-unselectable">
    <div class="card-content card-content-compact">
      <div class="title is-6 has-text-centered" v-html="text"></div>
      <div class="columns is-gapless" style="margin-bottom: 10px;">
        <div class="column is-narrow">{{leftValue}}&nbsp;</div>
        <div class="column">
          <div :style="{ 'height': '20px', 'background-image': `linear-gradient(to right, ${gradient})`, 'border': '1px solid gray'}"></div>
        </div>
        <div class="column is-narrow">&nbsp;{{rightValue}}</div>
      </div>
      <div class="has-text-centered">
        <span :style="{'padding': '0 8px', 'min-width': '20px', 'border': '1px solid gray', 'background': `${nacolor}` }"></span>
        &nbsp;{{natext}}
      </div>
    </div>
  </div>
</template>


<script>

import { singleColors, notDetectedColor } from '@/expression-sources/hpa';

export default {
  name: 'RNALegend',
  props: {
    text: {
      default: 'log<sub>2</sub>(TPM+1)',
    },
    gradient: {
      default: `${singleColors}`,
    },
    leftValue: {
      default: '0',
    },
    rightValue: {
      default: '7+',
    },
    nacolor: {
      default: `${notDetectedColor}`,
    },
    natext: {
      default: 'n/a',
    },
  },
};

</script>

<style lang="scss"></style>
