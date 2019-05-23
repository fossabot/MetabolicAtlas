<template>
  <div v-if="selectedElm && ['enzyme', 'metabolite', 'reaction'].includes(selectedElm.type)" class="card">
    <header class="card-header">
      <p class="card-header-title">
        <span v-if="selectedElm.type === 'reaction'">
          Reaction ID: {{ selectedElm.id }}
        </span>
        <span v-else class="is-capitalized">
          {{ selectedElm.type }}
          <router-link :to="{ path: `/explore/gem-browser/${this.model.database_name}/${selectedElm.type}/${this.selectedElm.real_id || this.selectedElm.id}` }">
            {{ selectedElm.name }}
          </router-link>
        </span>
      </p>
    </header>
  </div>
</template>

<script>

import { default as messages } from '../../../helpers/messages';

export default {
  name: 'sidebar',
  props: ['model', 'selectedElm'],
  data() {
    return {
      messages,
    };
  },
};
</script>

<style lang="scss">
</style>
