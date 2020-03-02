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
        :to="{ name: 'interPartner',  params: { model: model.database_name, id: selectedElm.real_id || selectedElm.id } }">  <!-- eslint-disable-line max-len -->
        <span class="icon is-large"><i class="fa fa-share-alt fa-lg"></i></span>
        <span>{{ messages.interPartName }}</span>
      </router-link>
      <router-link
        class="is-paddingless is-info is-outlined card-footer-item has-text-centered"
        :to="{ name: 'browser', params: { model: model.database_name, type: selectedElm.type, id: selectedElm.real_id || selectedElm.id } }">  <!-- eslint-disable-line max-len -->
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
