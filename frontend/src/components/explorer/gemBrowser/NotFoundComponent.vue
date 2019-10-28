<template>
  <div class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile has-text-centered">
    <div class="box has-background-light content">
      <p class="title is-size-3">
        <span class="is-capitalized">{{ component }}&nbsp;</span> "&nbsp;{{ componentID }}&nbsp;" &nbsp;not found
      </p>
      <p class="is-size-5">
        Probably there is a typo in the {{ component }} identifier in the URL
        <br>Use the search bar to find other {{ component }}s
      </p>
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
