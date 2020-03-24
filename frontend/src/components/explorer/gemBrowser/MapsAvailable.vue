<template>
  <div class="card" title="Click on any of the links to directly load a map">
    <header class="card-header has-text-centered">
      <p class="card-header-title has-text-primary has-text-weight-bold is-size-5">
        <span class="icon is-medium"><i class="fa fa-map-o"></i></span>&nbsp;
        <span>{{ messages.mapViewerName }}</span>
      </p>
    </header>
    <div v-if="mapsAvailable" class="card-content" style="padding: 0.5rem;">
      <div v-for="mapKey in ['2d', '3d']"
           :key="mapKey"
           class="content has-text-left is-paddingless" style="padding-bottom: 1rem">
        <template v-if="mapsAvailable[mapKey]['count'] !== 0">{{ mapKey.toUpperCase() }} maps
          <ul style="margin: 0 1rem">
            <template v-for="map in mapsAvailable[mapKey]['compartment'].concat(mapsAvailable[mapKey]['subsystem'])">
              <li :key="map[0]">
                <!-- eslint-disable-next-line max-len -->
                <router-link :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${elementID}?dim=${mapKey}` }">
                  {{ map[1] }}
                </router-link>
              </li>
            </template>
          </ul>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'MapsAvailable',
  props: {
    type: String,
    id: String,
    elementID: String,
  },
  data() {
    return {
      mapsAvailable: '',
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
  beforeMount() {
    axios.get(`${this.model.database_name}/available_maps/${this.type}/${this.id}`)
      .then((response) => {
        this.mapsAvailable = response.data;
      }).catch(() => {
      });
  },
};
</script>

<style lang="scss"></style>
