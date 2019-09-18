<template>
  <div class="column is-one-fifth-widescreen is-one-quarter-desktop
              is-one-quarter-tablet is-half-mobile has-background-lightgray"
       style="padding-left: 0; overflow-y: auto;">
    <button class="button is-fullwidth" @click="loadeComponent='GeneExpression'">Gene Expression</button>
    <button class="button is-fullwidth" @click="loadeComponent='ReactionFluxes'">Reaction fluxes</button>
    <button class="button is-fullwidth" @click="loadeComponent='MetaboliteData'">Metabolites</button>
    <div class="columns">
      <component
        :is="loadeComponent"
        :model="model"
        :map-type="mapType"
        :map-name="mapName"
        :dim="dim">
      </component>
    </div>
  </div>
</template>

<script>
import GeneExpression from '@/components/explorer/mapViewer/dataOverlay/GeneExpression.vue';
import ReactionFluxes from '@/components/explorer/mapViewer/dataOverlay/ReactionFluxes.vue';
import MetaboliteData from '@/components/explorer/mapViewer/dataOverlay/MetaboliteData.vue';

export default {
  name: 'DataOverlay',
  components: {
    GeneExpression,
    ReactionFluxes,
    MetaboliteData,
  },
  props: {
    model: Object,
    mapType: String,
    mapName: String,
    dim: String,
  },
  data() {
    return {
      loadeComponent: 'GeneExpression',
    };
  },
  methods: {
  },
};
</script>

<style lang="scss">
</style>
