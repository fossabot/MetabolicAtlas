<template>
  <div class="card card-margin is-unselectable"> <!-- fix card-margin -->
    <div class="card-content card-content-compact">
      <div class="title is-6 has-text-centered" v-html="text"></div>
      <div class="columns is-gapless" style="margin-bottom: 10px;">
        <div class="column is-narrow">{{ leftValue }}&nbsp;</div>
        <div class="column">
          <div :style="{ 'height': '20px',
                         'background-image': `linear-gradient(to right, ${gradient})`,
                         'border': '1px solid gray'}"></div>
        </div>
        <div class="column is-narrow">&nbsp;{{ rightValue }}</div>
      </div>
      <div class="has-text-centered">
        <span :style="{'padding': '0 8px', 'min-width': '20px',
                       'border': '1px solid gray', 'background': `${nacolor}` }"></span>
        &nbsp;{{ natext }}
      </div>
    </div>
  </div>
</template>


<script>

export default {
  name: 'Legend',
  props: {
    text: {
      type: String,
    },
    gradient: {
      type: String,
    },
    leftValue: {
      type: String,
    },
    rightValue: {
      type: String,
    },
    nacolor: {
      type: String,
    },
    natext: {
      type: String,
    },
  },
};

</script>

<style lang="scss"></style>
