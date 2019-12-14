<template>
  <section class="section extended-section">
    <div class="columns is-centered">
      <notFoundComponent></notFoundComponent>
    </div>
  </section>
</template>

<script>

import NotFoundComponent from '@/components/explorer/gemBrowser/NotFoundComponent';

export default {
  name: 'NotFound',
  components: {
    NotFoundComponent,
  },
};

</script>

<style>
</style>
