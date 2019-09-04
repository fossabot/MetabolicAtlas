<template>
  <div class="card is-unselectable">
    <div class="card-content card-content-compact">
      <div class="title is-6 has-text-centered" v-html="text"></div>
      <div class="columns is-gapless" style="margin-bottom: 10px;">
        <div class="column is-narrow">{{leftValue}}&nbsp;</div>
        <div class="column">
          <div :style="{ 'height': '20px', 'background-image': `linear-gradient(to right, ${gradient})`}"></div>
        </div>
        <div class="column is-narrow">&nbsp;{{rightValue}}</div>
      </div>
      <div class="has-text-centered">
        <span :style="{'padding': '0.15rem 0.70rem', 'min-width': '20px', 'border': '1px solid black', 'background': `${nacolor}` }"></span>
        &nbsp;{{natext}}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RNALegend',
  props: {
    text: {
      default: 'log<sub>2</sub>(TPM+1)',
    },
    gradient: {
      default: '#FFFFFF, #ffe945',
    },
    leftValue: {
      default: '0',
    },
    rightValue: {
      default: '7+',
    },
    nacolor: {
      default: 'lightgray',
    },
    natext: {
      default: 'n/a',
    },
  },
};

</script>

<style lang="scss"></style>
