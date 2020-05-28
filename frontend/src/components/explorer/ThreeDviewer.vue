<template>
  <div class="extended-section">
    <div id="iMainPanel" class="columns">
      <template v-if="errorMessage">
        <div class="column">
          <div class="columns">
            <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
              <p>{{ errorMessage }}</p>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div id="viewer" class="atlas-viewer"></div>
      </template>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import { mapState } from 'vuex';
import { MetAtlasViewer } from '@metabolicatlas/mapviewer-3d';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'ThreeDViewer',
  data() {
    return {
      errorMessage: '',
      messages,
      controller: null,
      data: {},
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
  mounted() {
    this.controller = MetAtlasViewer('viewer');
    const frontenPublic = axios.create({ baseURL: '/' });
    frontenPublic.get('/data-colors.js')
      .then((response) => {
        this.data = response.data;
        this.controller.setData(
          this.data,
          [{ group: 'e', sprite: '/sprite_round.png' },
            { group: 'r', sprite: '/sprite_square.png' },
            { group: 'm', sprite: '/sprite_triangle.png' }],
          15);
      });
    // console.log('controller:', controller);
    // controller.filterBy({group: 'm'});
    // controller.filterBy({id: [1, 2, 3, 4]});
    // Subscribe to node selection events
    // document.getElementById('viewer').addEventListener('select', e => console.debug('selected', e.detail));
  },
};
</script>

<style lang='scss'>
.atlas-viewer {
  margin: 0;
  padding: 0;
}
</style>
