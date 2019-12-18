<template>
  <div>
    <br>
    <article class="message">
      <!-- <div class="message-header"> -->
      <a class="button is-grey is-fullwidth" @click="isExpanded = ! isExpanded">
        <span class="icon"><i class="fa fa-question fa-lg"></i></span>&nbsp;
        <span>Report an issue</span>
      </a>
      <!-- </div> -->
      <div v-if="isExpanded" class="message-body has-text-justified">
        Get in touch with the authors of {{ model }} to tell them what is wrong with this {{ type }}
        <a :href="`mailto:${{ email }}?subject=whatever%20page%20i%20am%20on&body=Hello`">via email</a>
        <template v-if="chatLink">
          or <a :href="chatLink" target="_blank">via public chat (faster)</a>
        </template>.
      </div>
    </article>
  </div>
</template>

<script>
export default {
  name: 'GemContact',
  props: {
    email: {
      type: String,
      required: true,
    },
    chatLink: {
      type: String,
      required: false,
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
