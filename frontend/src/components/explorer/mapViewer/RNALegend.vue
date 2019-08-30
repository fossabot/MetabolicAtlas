<template>
  <div class="card">
    <div class="card-content card-content-compact">
      <div class="title is-6 has-text-centered" v-html="text"></div>
      <div class="has-text-centered">
        {{leftValue}}&nbsp;
        <div :style="{ 'height': '20px', 'background-image': `linear-gradient(to right, ${leftColor}, ${rightColor})` }"></div>
        &nbsp;{{rightValue}}
        <div style="width: 15px; height: 15px; border: 1px solid black; background: ${notDetectedSingleColor};"></div>
        <span>n/a</span>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'RNALegend',
  props: ['text', 'leftValue', 'rightValue', 'leftColor', 'rightColor', 'nacolor', 'natext'],
};

</script>

<style lang="scss"></style>
