<template>
  <div class="column is-12">
    <div class="card">
      <header class="card-header clickable is-unselectable" @click.prevent="showCardContent = !showCardContent">
        <p class="card-header-title is-size-5">
          {{ panelData.title }}
        </p>
        <a class="card-header-icon" aria-label="more options">
          <span class="icon">
            <i :class="[showCardContent ? 'fa-caret-down' : 'fa-caret-right', 'fa']" aria-hidden="true"></i>
          </span>
        </a>
      </header>
      <div v-show="showCardContent" class="card-content card-content-compact is-paddingless has-background-lightgray">
        <OverlayDataModule v-if="panelData.dataSources" :model="model" :panel-data="panelData"
          :map-type="mapType" :map-name="mapName" :dim="dim">
        </OverlayDataModule>
      </div>
    </div>
  </div>
</template>

<script>

import OverlayDataModule from '@/components/explorer/mapViewer/dataOverlay/OverlayDataModule.vue';

export default {
  name: 'DataOverlayPanel',
  props: {
    component: String,
    model: Object,
    mapType: String,
    mapName: String,
    dim: String,
    panelData: Object,
  },
  components: {
    OverlayDataModule,
  },
  data() {
    return {
      showCardContent: false,
    };
  },
};
</script>

<style lang="scss">
</style>
