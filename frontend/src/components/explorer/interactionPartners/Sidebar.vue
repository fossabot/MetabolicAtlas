<template>
  <div v-if="selectedElm && ['gene', 'metabolite', 'reaction'].includes(selectedElm.type)" class="card">
    <header class="card-header">
      <p class="card-header-title">
        <span class="is-capitalized">
          {{ selectedElm.type }}: {{ selectedElm.name || selectedElm.id }}
          <span v-if="selectedElm.type === 'metabolite'" class="has-text-weight-light has-text-grey-light">
            {{ selectedElm.compartment }}
          </span>
        </span>
      </p>
    </header>
    <footer class="card-footer has-text-centered">
      <router-link
        v-if="!onlyGB && selectedElm.type !== 'reaction'"
        class="card-footer-item is-paddingless"
        :to="{ path: `/explore/interaction/${model.database_name}/${elmId}` }">
        <span class="icon is-large"><i class="fa fa-share-alt fa-lg"></i></span>
        <span>{{ messages.interPartName }}</span>
      </router-link>
      <router-link
        class="card-footer-item is-paddingless"
        :to="{ path: `/explore/gem-browser/${model.database_name}/${selectedElm.type}/${elmId}` }">  <!-- eslint-disable-line max-len -->
        <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
        <span>{{ messages.gemBrowserName }}</span>
      </router-link>
    </footer>
  </div>
</template>

<script>

import { default as messages } from '@/helpers/messages';

export default {
  name: 'Sidebar',
  props: {
    model: Object,
    selectedElm: Object,
    onlyGB: Boolean,
  },
  computed: {
    elmId() {
      return this.selectedElm.real_id || this.selectedElm.id;
    },
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
