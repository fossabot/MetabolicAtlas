<template>
  <div v-if="selectedElm && ['gene', 'metabolite', 'reaction'].includes(selectedElm.type)" class="card">
    <header class="card-header">
      <p class="card-header-title">
        <span class="is-capitalized">
          {{ selectedElm.type }}: {{ selectedElm.name || selectedElm.id }}
          <span v-if="selectedElm.type === 'metabolite'" class="is-size-7 has-text-grey">
            {{ selectedElm.compartment }}
          </span>
        </span>
      </p>
    </header>
    <footer class="card-footer">
      <router-link
        v-if="selectedElm.type !== 'reaction'"
        class="is-paddingless is-info is-outlined card-footer-item has-text-centered"
        :to="{ path: `/explore/interaction/${model.database_name}/${selectedElm.real_id || selectedElm.id}` }">
        <span class="icon is-large"><i class="fa fa-share-alt fa-lg"></i></span>
        <span>{{ messages.interPartName }}</span>
      </router-link>
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

import { mapState } from 'vuex';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Sidebar',
  props: {
    selectedElm: Object,
  },
  data() {
    return {
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
};
</script>

<style lang="scss">
</style>
