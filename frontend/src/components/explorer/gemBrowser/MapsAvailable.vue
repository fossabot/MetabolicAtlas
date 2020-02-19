<template>
  <div class="card" title="Click on any of the links to directly load a map" >
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
            <template v-for="map in mapsAvailable[mapKey]['compartment'].concat(mapsAvailable[mapKey]['subsystem'])">
              <li :key="map[0]">
                <router-link v-if="viewerSelectedID" :to="{ name: 'viewer', params: { model: model.database_name, type: mapType, map_id: map[0] }, query: { dim: mapKey, search: viewerSelectedID, sel: viewerSelectedID } }">
                {{ map[1] }}
                </router-link>
                <!-- eslint-disable-next-line max-len -->
                <router-link v-else :to="{ name: 'viewer', params: { model: model.database_name, type: mapType, map_id: map[0]}, query: { dim: mapKey } }">
                {{ map[1] }}
              </li>
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
import axios from 'axios';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'MapsAvailable',
  props: {
    model: Object,
    type: String,
    id: String,
    viewerSelectedID: String,
  },
  data() {
    return {
      mapsAvailable: '',
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
    mapAvailableLimited() {
      if (!this.mapsAvailable) {
        return '';
      }
      const limited = JSON.parse(JSON.stringify(this.mapsAvailable)); // copy
      ['2d', '3d'].forEach((d) => {
        let remainingEntries = this.mapLimitPerDim;
        ['compartment', 'subsystem'].forEach((t) => {
          if (limited[d][t].length > remainingEntries) {
            this.limitedMapsDim[d] = true; // eslint-disable-line vue/no-side-effects-in-computed-properties
            limited[d][t] = limited[d][t].slice(0, remainingEntries);
          } else {
            this.limitedMapsDim[d] = false; // eslint-disable-line vue/no-side-effects-in-computed-properties
          }
          remainingEntries -= limited[d][t].length;
        });
      });
      return limited;
    },
  },
  watch: {
    id() {
      this.mapsAvailable = '';
      this.mapLimitPerDim = 4;
      this.getAvailableMaps();
    },
  },
  created() {
    this.getAvailableMaps();
  },
  methods: {
    getAvailableMaps() {
      axios.get(`${this.model.database_name}/available_maps/${this.type}/${this.id}`)
        .then((response) => {
          this.mapsAvailable = response.data;
        }).catch(() => {
        });
    },
  },
};
</script>

<style lang="scss"></style>
