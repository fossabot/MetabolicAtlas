<template>
  <div v-if="selectedElm && ['gene', 'metabolite', 'reaction'].includes(selectedElm.type)" class="card">
    <header class="card-header">
      <p class="card-header-title">
        <span class="is-capitalized">
          {{ selectedElm.type }}: {{ selectedElm.name || selectedElm.id }}
        </span>
      </p>
    </header>
    <footer class="card-footer">
      <router-link
        class="is-paddingless is-info is-outlined card-footer-item has-text-centered"
        :to="{ path: `/explore/gem-browser/${model.database_name}/${selectedElm.type}/${selectedElm.real_id || selectedElm.id}` }">  <!-- eslint-disable-line max-len -->
        <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
        <span>{{ messages.gemBrowserName }}</span>
      </router-link>
    </footer>
  </div>
</template>

<script>

import { default as messages } from '../../../helpers/messages';

export default {
  name: 'Sidebar',
  props: {
    model: Object,
    selectedElm: Object,
  },
  data() {
    return {
      messages,
    };
  },
};
</script>

<style lang="scss">
</style>
