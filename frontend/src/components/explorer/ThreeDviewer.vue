<template>
  <div id="3DViewer" class="extended-section">
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
        <div class="title">Metabolic Atlas 3D Map Viewer, demo.</div>
      </template>
    </div>
  </div>
</template>

<script>
// import $ from 'jquery';
// import axios from 'axios';
// import { default as EventBus } from '../../event-bus';
// import { MetAtlasViewer } from '@/components/explorer/threeDviewer/met-atlas-viewer';
import { default as messages } from '../../helpers/messages';

export default {
  name: 'ThreeDViewer',
  props: {
    model: Object,
  },
  data() {
    return {
      errorMessage: '',
      controller: null,
      data: null,
      messages,
    };
  },
  mounted() {
    // console.log(this.$metAtlasViewer);
    this.controller = this.$metAtlasViewer.MetAtlasViewer('viewer');

    // Add stats
    // const stats = new Stats();
    // document.getElementById('viewer').appendChild(stats.domElement);
    // requestAnimationFrame(
    //     function loop() {stats.update(); requestAnimationFrame(loop)}
    // );

    this.data = this.makeData(1000);
    this.controller.setData(this.data, [{ group: 'e', sprite: 'sprite_round.png' },
      { group: 'r', sprite: 'sprite_square.png' },
      { group: 'm', sprite: 'sprite_triangle.png' }], 15);

    // filter selection examples: (available after the graph has
    // initialized)
    //
    // controller.filterBy({group: 'm'});
    // controller.filterBy({id: [1, 2, 3, 4]});
    //
    // write a reference of the controller to the log for testing:
    console.log('controller:', this.controller);

    // Subscribe to node selection events
    document.getElementById('viewer').addEventListener('select',
      ($event) => { console.debug('selected', $event.detail); });
  },
  methods: {
    makeData(numberOfNodes = 100, radius = 2000, nice = true) {
      console.log('make data');
      function randomInSphere(r) {
        let z = 2 * Math.random() - 1;
        const theta = 2 * Math.PI * Math.random();
        const R = 1 - 1 / (Math.exp(5 * Math.random()));
        const x = R * (Math.sqrt(1 - z * z) * Math.cos(theta)) * r;
        const y = R * (Math.sqrt(1 - z * z) * Math.sin(theta)) * r;
        z = R * z * r;
        return [x, y, z];
      }
      const start = Date.now();
      const data = { nodes: [], links: [] };
      for (let i = 0; i < numberOfNodes; i += 1) {
        console.log(i);
        const pos = randomInSphere(radius);
        const color = [Math.floor(255 * (pos[0] - radius) / (2 * radius)),
          Math.floor(255 * (pos[1] - radius) / (2 * radius)),
          Math.floor(255 * (pos[2] - radius) / (2 * radius)),
        ];
        data.nodes.push({ id: i, pos, color, g: ['e', 'r', 'm'][Math.floor(Math.random() * 3)] });
        if (i > 0) {
          if (!nice) {
            data.links.push({ s: i, t: Math.floor((Math.random() * i)) });
            continue; // eslint-disable-line no-continue
          }
          let index = 0;
          let closest = radius + 1;
          const a = data.nodes[i];
          for (let j = 0; j < i; j += 1) {
            const b = data.nodes[j];
            const x = Math.abs(a.pos[0] - b.pos[0]);
            const y = Math.abs(a.pos[1] - b.pos[1]);
            const z = Math.abs(a.pos[2] - b.pos[2]);
            const distance = Math.sqrt(x * x + y * y + z * z);
            if (distance < closest) {
              closest = distance;
              index = j;
            }
          }
          data.links.push({ s: i, t: index });
        }
      }
      console.log(`Generated a ${nice ? 'nice ' : ''} graph of ${numberOfNodes} nodes in ${new Date() - start} ms.`);
      return data;
    },
  },
};
</script>

<style lang='scss'>
  .title {
    position: fixed;
    top: 0;
    left: 85px;
    font-family: 'Courier New', Courier, monospace;
  }
  .atlas-viewer {
    padding: 0;
    margin: 0;
  }
</style>
