<template>
  <article class="message">
    <!-- <div class="message-header"> -->
    <a class="button is-grey is-fullwidth" @click="isExpanded = ! isExpanded">
      <span class="icon"><i class="fa fa-question fa-lg"></i></span>&nbsp;
      <span>Wrong data</span>
    </a>
    <!-- </div> -->
    <div v-if="isExpanded" class="message-body has-text-justified">
      <a :href="link" target="_blank">
        Click here to get in touch with the authors of {{ model }} and tell them what is wrong with this {{ type }}
      </a>
    </div>
  </article>
</template>

<script>
export default {
  name: 'GemContact',
  props: {
    link: {
      type: String,
      required: true,
    },
    model: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isExpanded: false,
    };
  },
};
</script>

<style lang="scss"></style>
