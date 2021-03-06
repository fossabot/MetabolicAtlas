<template>
  <div class="card" title="Click on any of the links to directly load a map">
    <header class="card-header has-text-centered">
      <p class="card-header-title has-text-primary has-text-weight-bold is-size-5">
        <span class="icon is-medium"><i class="fa fa-map-o"></i></span>&nbsp;
        <span>{{ messages.mapViewerName }}</span>
      </p>
    </header>
    <!-- eslint-disable-next-line max-len -->
    <div v-if="mapAvailableLimited" class="card-content" style="padding: 0.5rem; overflow-y: auto; max-height: 400px">
      <div v-for="mapKey in ['2d', '3d']" :key="mapKey"
           class="content has-text-left is-paddingless" style="padding-bottom: 1rem">
        <!-- eslint-disable-next-line max-len -->
        <template v-if="mapAvailableLimited[mapKey]['compartment'].length !== 0 || mapAvailableLimited[mapKey]['subsystem'].length !== 0">{{ mapKey.toUpperCase() }} maps
          <ul style="margin: 0 1rem">
            <template v-for="mapType in Object.keys(mapAvailableLimited[mapKey])">
              <template v-for="map in mapAvailableLimited[mapKey][mapType]">
                <li :key="map[0]">
                  <!-- eslint-disable-next-line max-len -->
                  <router-link v-if="viewerSelectedID" :to="{ name: 'viewer', params: { model: model.database_name, type: mapType, map_id: map[0], reload: true }, query: { dim: mapKey, search: viewerSelectedID, sel: viewerSelectedID } }">
                    {{ map[1] }}
                  </router-link>
                  <!-- eslint-disable-next-line max-len -->
                  <router-link v-else :to="{ name: 'viewer', params: { model: model.database_name, type: mapType, map_id: map[0]}, query: { dim: mapKey } }">
                    {{ map[1] }}
                  </router-link>
                </li>
              </template>
            </template>
            <!-- eslint-disable-next-line max-len -->
            <li v-if="limitedMapsDim[mapKey]" class="clickable" title="View all maps" @click="mapLimitPerDim = 1000">...</li>
          </ul>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'MapsAvailable',
  props: {
    type: String,
    id: String,
    viewerSelectedID: String,
  },
  data() {
    return {
      messages,
      mapLimitPerDim: 4,
      limitedMapsDim: {
        '2d': false,
        '3d': false,
      },
      limited3DMaps: false,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      mapsAvailable: state => state.maps.availableMaps,
    }),
    mapAvailableLimited() {
      /* eslint-disable vue/no-side-effects-in-computed-properties */
      // TODO: move this into vuex
      if (Object.keys(this.mapsAvailable).length === 0) {
        return null;
      }
      const limited = JSON.parse(JSON.stringify(this.mapsAvailable)); // copy
      ['2d', '3d'].forEach((d) => {
        this.limitedMapsDim[d] = false;
        if (limited[d].compartment.length > this.mapLimitPerDim) {
          this.limitedMapsDim[d] = true;
          limited[d].compartment = limited[d].compartment.slice(0, this.mapLimitPerDim);
          limited[d].subsystem = [];
        } else {
          const remainingEntries = this.mapLimitPerDim - limited[d].compartment.length;
          if (limited[d].subsystem.length > remainingEntries) {
            limited[d].subsystem = limited[d].subsystem.slice(0, remainingEntries);
            this.limitedMapsDim[d] = true;
          }
        }
      });
      /* eslint-enable vue/no-side-effects-in-computed-properties */
      return limited;
    },
  },
  async beforeMount() {
    try {
      const payload = { model: this.model.database_name, mapType: this.type, id: this.id };
      await this.$store.dispatch('maps/getAvailableMaps', payload);
    } catch {
      // TODO: handle exception
    }
  },
};
</script>

<style lang="scss"></style>
