<template>
  <div class="column is-narrow has-text-centered">
    <div class="box notification content">
      <p class="is-size-5">No {{ component }} found for identifier <i>{{ componentID }}</i></p>
      <p>Use the search bar to find other {{ component }}s</p>
    </div>
  </div>
</template>
<script>

// import { default as messages } from '../../../helpers/messages';

export default {
  name: 'NotFoundComponent',
  props: {
    component: String,
    componentID: String,
  },
};

</script>

<style>
</style>
