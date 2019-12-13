<template>
  <div ref="graphParent">
    <div id="graph3D"></div>
    <div class="canvasOption overlay">
      <span class="button" title="Download as PNG" @click="downloadPNG()"><i class="fa fa-download"></i></span>
    </div>
    <MapSearch ref="mapsearch" :model="model" :matches="searchedNodesOnGraph" :ready="graph !== null"
               @searchOnMap="searchIDsOnGraph" @centerViewOn="focusOnNode"
               @unHighlightAll="unHighlight"></MapSearch>
  </div>
</template>

<script>

import axios from 'axios';
import forceGraph3D from '3d-force-graph';
import { default as FileSaver } from 'file-saver';
import MapSearch from '@/components/explorer/mapViewer/MapSearch';
import { default as EventBus } from '../../../event-bus';
import { reformatChemicalReactionHTML } from '../../../helpers/utils';

// const THREE = require('three'); // eslint-disable-line import/no-extraneous-dependencies

export default {
  name: 'D3dforce',
  components: {
    MapSearch,
  },
  props: {
    model: Object,
  },
  data() {
    return {
      errorMessage: '',
      loadedComponentType: null,
      loadedComponentName: null,
      graph: null,
      // emptyNetwork: true,
      networkHistory: {},
      network: {
        nodes: [],
        links: [],
      },

      selectIDs: [],
      selectedItemHistory: {},
      selectElementID: null,
      selectElementIDfull: null,

      searchIDsSet: new Set(),
      searchedNodesOnGraph: [],

      coords: null,

      HPARNAlevels: {},
      defaultGeneColor: '#feb',
      tissue: 'None',
      focusOnID: null,
      searchTerm: '',

      listenControl: false,
      disableControlsListener: false,
    };
  },
  watch: {
    graph(v) {
      console.log('graph changed -=========');
      if (v === null) {
        this.listenControl = false;
      } else if (!this.listenControl) {
        this.listenControl = true;
        // use debounce TODO
        v.controls()
          .addEventListener('change', (ev) => {
            if (this.disableControlsListener) {
              this.disableControlsListener = false;
              return;
            }
            const pos = ev.target.object.position; // eslint-disable-line no-unused-vars
            const { lookAt } = this.graph.cameraPosition(); // eslint-disable-line no-unused-vars
            const rot = this.graph.camera().rotation; // eslint-disable-line no-unused-vars
            // console.log(this.graph.camera());
            const { up } = this.graph.camera(); // eslint-disable-line no-unused-vars

            // const { target } = v.controls();
            console.log('loadedComponentName', this.loadedComponentName);
            EventBus.$emit('update_url_coord', pos.x, pos.y, pos.z,
              lookAt.x, lookAt.y, lookAt.z,
              rot.x, rot.y, rot.z,
              up.x, up.y, up.z);
            // console.log(v.controls());
          });
      }
    },
  },
  created() {
    EventBus.$off('show3Dnetwork');
    EventBus.$off('destroy3Dnetwork');
    EventBus.$off('update3DLoadedComponent');
    EventBus.$off('apply3DHPARNAlevels');
    EventBus.$off('recompute3DCanvasBounds');

    EventBus.$on('show3Dnetwork', (type, name, searchTerm, selectIDs, coords, force) => {
      console.log('show3Dnetwork', type, name, searchTerm, selectIDs, coords, force);
      if (force) {
        this.loadedComponentName = null;
      }
      if (name.toLowerCase().substr(0, 7) === 'cytosol') {
        name = 'cytosol'; // eslint-disable-line no-param-reassign
      }
      this.searchTerm = searchTerm;
      // if (searchIDs && searchIDs.length === 1) {
      //   this.focusOnID = searchIDs[0]; // eslint-disable-line prefer-destructuring
      // } else {
      //   // do not handle multiple ids for now;
      //   this.focusOnID = null;
      // }
      this.selectIDs = selectIDs.length !== 0 ? selectIDs : [];
      this.coords = coords !== '0,0,0,0,0,0,0,0,0,0,0,0' ? coords : null; // FIXME
      if (this.loadedComponentType !== type || this.loadedComponentName !== name) {
        // reset some values
        this.selectElementID = null;
        this.selectElementIDfull = null;
        this.$refs.mapsearch.reset();
        if (this.graph) {
          this.coords = null;
        }
        console.log('build network');
        // console.log('this.emptyNetwork', this.emptyNetwork);
        console.log(this.loadedComponentType, type);
        console.log(this.loadedComponentName, name);
        this.loadedComponentType = type;
        this.loadedComponentName = name;
        if (name in this.networkHistory) {
          console.log('from history ===');
          this.$emit('loading');
          this.graph.resetCamera = true;
          this.graph.reloadHistory = true;
          this.network = this.networkHistory[name];
          this.graph.graphData(this.network);
        } else {
          this.getJson();
        }
      } else if (this.focusOnID) {
        this.graph.emitLoadComplete = true;
        // get the first node matching
        const nodes = this.graph.graphData().filter(n => n.id.split('-')[0] === this.focusOnID);
        this.focusOnNode(nodes.length !== 0 ? nodes[0] : null);
      } else {
        this.$emit('loadComplete', true, '');
      }
    });

    EventBus.$on('destroy3Dnetwork', () => {
      if (this.graph) {
        this.graph.graphData({ nodes: [], links: [] });
        this.loadedComponentName = '';
        this.loadedComponentType = '';
      }
    });

    EventBus.$on('update3DLoadedComponent', (type, name) => {
      this.loadedComponentType = type;
      this.loadedComponentName = name;
    });

    EventBus.$on('recompute3DCanvasBounds', () => {
      if (!this._inactive && this.graph) { // eslint-disable-line no-underscore-dangle
        this.updateGeometries();
      }
    });

    EventBus.$on('apply3DHPARNAlevels', (RNAlevels) => {
      this.applyHPARNAlevelsOnMap(RNAlevels);
    });
  },
  methods: {
    getJson() {
      this.$emit('loading');
      this.HPARNAlevels = {};
      axios.get(`/${this.model.database_name}/json/${this.loadedComponentType}/${this.loadedComponentName}`)
        .then((response) => {
          this.network = response.data;
          setTimeout(() => {
            if (this.graph === null) {
              this.graph = {};
              this.graph.emitLoadComplete = true;
              this.graph.resetCamera = true;
              this.constructGraph();
            } else {
              this.graph.resetCamera = true;
              this.graph.graphData(this.network);
            }
            // this.emptyNetwork = false;
          }, 0);
        })
        .catch((error) => {
          this.$emit('loadComplete', false, error, 'danger');
        });
    },
    constructGraph() {
      /* eslint-disable no-param-reassign */
      this.graph = forceGraph3D()(document.getElementById('graph3D'))
        .showNavInfo(false)
        .nodeLabel('n')
        .linkSource('s')
        .linkTarget('t')
        .forceEngine('ngraph')
        .graphData({ nodes: this.network.nodes, links: this.network.links })
        .nodeOpacity(1)
        .linkWidth(0)
        .linkOpacity(0.35)
        .nodeResolution(12)
        .warmupTicks(100)
        .cooldownTicks(0)
        .onNodeClick((n) => {
          this.selectElement(n);
        })
        .nodeColor((n) => {
          const partialID = n.id.split('-')[0];
          if (partialID === this.selectElementID) {
            return 'red';
          }
          if (this.searchIDsSet.size !== 0 && this.searchIDsSet.has(partialID)) {
            return 'blue';
          }
          if (n.g === 'e') {
            if (Object.keys(this.HPARNAlevels).length === 0) {
              return this.defaultGeneColor;
            }
            if (this.HPARNAlevels[partialID] !== undefined) {
              return this.HPARNAlevels[partialID][0];
            }
            return this.HPARNAlevels['n/a'][0];
          } if (n.g === 'r') {
            return '#fff';
          }
          return '#9df';
        })
        .onEngineStop(() => {
          if (this.graph === null
            || this.graph.reloadHistory === undefined
            || !this.graph.reloadHistory) {
            this.networkHistory[this.loadedComponentName] = this.network;
          }
          if (this.graph.resetCamera) {
            this.graph.resetCamera = false;
            this.resetCameraPosition();
          }
          this.updateGraphBounds();
          if (this.graph !== null
            && this.graph.emitLoadComplete !== undefined
            && !this.graph.emitLoadComplete) {
            this.graph.emitLoadComplete = true;
            console.log('emit 3D complete');
            // this.graph.emitLoadComplete is used to prevent to emit multiple time 'loadComplete'
            // which should be send only when the graph has been loaded for the first time
            // the value is reset to true, so if not specify to false, the event will be emited
            // e.g. when reusing the history
          } else if (this.graph.graphData().nodes.length !== 0) {
            if (this.coords) {
              const coords = this.coords.split(',').map(v => parseFloat(v));
              // console.log('move camera position', coords[0], coords[1], coords[2], coords[3], coords[4], coords[5]);
              this.moveCameraPosition(coords[0], coords[1], coords[2], coords[3], coords[4],
                coords[5], coords[6], coords[7], coords[8], coords[9], coords[10], coords[11]);
              // clear coords, programmatic move is only performed once
              this.coords = null;
            } else {
              console.log('no coord provided');
              EventBus.$emit('update_url_coord', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
            }
            this.$emit('loadComplete', true, '');
            console.log(this.graph.camera());
          }
          if (this.focusOnID) {
            const nodes = this.graph.graphData().filter(n => n.id.split('-')[0] === this.focusOnID);
            this.focusOnNode(nodes.length !== 0 ? nodes[0] : null);
          }
          if (this.selectIDs.length !== 0 && this.selectIDs[0] !== this.selectElementID) {
            let node = this.graph.graphData().nodes.filter(n => n.id.split('-')[0].toLowerCase() === this.selectIDs[0].toLowerCase());
            node = node[0]; // eslint-disable-line prefer-destructuring
            // console.log('node', node);
            // console.log('clean selectIDs');
            this.selectIDs = [];
            this.selectElement(node);
          }
          if (this.searchTerm) {
            // EventBus.$emit('search_term', this.searchTerm);
            this.$refs.mapsearch.search(this.searchTerm);
            this.searchTerm = '';
          }
        });
    },
    updateGraphBounds() {
      setTimeout(() => {
        if (this.$refs.graphParent && this.$refs.graphParent.offsetParent) {
          const width = this.$refs.graphParent.offsetParent.offsetWidth; // FIXME
          const height = this.$refs.graphParent.offsetParent.offsetHeight; // FIXME
          if (this.graph.width() !== width || this.graph.height() !== height) {
            this.graph.width(width).height(height);
          }
        }
      }, 0);
    },
    downloadPNG() {
      window.requestAnimationFrame(() => {
        document.getElementById('graph3D')
          .getElementsByTagName('canvas')[0]
          .toBlob((blob) => {
            FileSaver.saveAs(blob, `${this.loadedComponentName}.png`);
          });
      });
    },
    searchIDsOnGraph(ids) {
      console.log('searchIDsOnGraph', ids);
      this.searchIDsSet = new Set(ids);
      this.searchedNodesOnGraph = this.graph.graphData().nodes.filter(n => this.searchIDsSet.has(n.id.split('-')[0]));
      console.log('searchedNodesOnGraph', this.searchedNodesOnGraph.length);
      this.focusOnNode(this.searchedNodesOnGraph.length !== 0 ? this.searchedNodesOnGraph[0] : null);
      this.updateGeometries();
    },
    getElementIdAndType(element) {
      if (element.g === 'r') {
        return [element.id, 'reaction'];
      } if (element.g === 'e') {
        return [element.id.split('-')[0], 'gene'];
      }
      return [element.id.split('-')[0], 'metabolite'];
    },
    selectElement(element) {
      if (!element) {
        return;
      }
      const [id, type] = this.getElementIdAndType(element);
      if (this.selectElementID === id) {
        console.log('call unselect 3d SE');
        this.unSelectElement();
        this.updateGeometries();
        return;
      }
      const selectionData = { type, data: null, error: false };
      this.selectElementID = id;
      this.selectElementIDfull = element.id;

      if (this.selectedItemHistory[id]) {
        selectionData.data = this.selectedItemHistory[id];
        this.updateGeometries();
        this.$emit('newSelection', selectionData);
        return;
      }

      this.$emit('startSelection');
      axios.get(`${this.model.database_name}/${type === 'reaction' ? 'get_reaction' : type}/${id}`)
        .then((response) => {
          let { data } = response;
          if (type === 'reaction') {
            data = data.reaction;
            data.equation = this.reformatChemicalReactionHTML(data, true);
          } else if (type === 'gene') {
            // add the RNA level if any
            if (id in this.HPARNAlevels) {
              data.rnaLvl = this.HPARNAlevels[id];
            }
          }
          selectionData.data = data;
          this.$emit('newSelection', selectionData);
          this.selectedItemHistory[id] = selectionData.data;
          this.$emit('endSelection', true);
          this.updateGeometries();
        })
        .catch(() => {
          this.$emit('endSelection', false);
        });
    },
    unSelectElement() {
      this.selectElementID = null;
      this.selectElementIDfull = null;
      this.$emit('unSelect');
    },
    focusOnNode(node) {
      if (!node) {
        return;
      }
      this.focusOnID = null;
      // this.unSelectElement();
      // let node = this.network.nodes.filter(n => n.id.toLowerCase() === id.toLowerCase());
      // if (node.length !== 1) {
      //   return;
      // }
      // node = node[0]; // eslint-disable-line prefer-destructuring
      // this.selectElement(node);
      const np = node.__threeObj.position; // eslint-disable-line no-underscore-dangle
      setTimeout(() => {
        const distance = 300;
        const distRatio = 1 + (distance / Math.hypot(np.x, np.y, np.z));
        this.graph.cameraPosition(
          {
            x: np.x * distRatio,
            y: np.y * distRatio,
            z: np.z * distRatio,
          },
          np, // lookAt ({ x, y, z })
          3000 // ms transition duration
        );
      }, 0);
    },
    moveCameraPosition(x, y, z, lx, ly, lz, tx, ty, tz, ux, uy, uz) { // eslint-disable-line no-unused-vars
      this.disableControlsListener = true;
      // console.log('rot new value', { x: tx, y: ty, z: tz });
      // console.log('up new value', { x: ux, y: uy, z: uz });
      // this.graph.camera().rotation.set(tx, ty, tz);
      // this.graph.camera().up.set(ux, uy, uz);
      // this.graph.camera().rotation.x = tx;
      // this.graph.camera().rotation.y = ty;
      // this.graph.camera().rotation.z = tz;
      this.graph.cameraPosition(
        { x, y, z },
        { x: lx, y: ly, z: lz }, // lookAt ({ x, y, z })
        0 // ms transition duration
      );
      // this.graph.controls().target = { x: tx, y: ty, z: tz };
      // this.graph.camera().updateProjectionMatrix();
      console.log(this.graph.camera());
    },
    resetCameraPosition() {
      this.moveCameraPosition(0, 0, Math.cbrt(this.graph.graphData().nodes.length) * 150, 0, 0, 0, 0, 0, 0);
      // this.graph.cameraPosition(
      //   { x: 0, y: 0, z: Math.cbrt(this.graph.graphData().nodes.length) * 150 },
      //   { x: 0, y: 0, z: 0 }, // lookAt ({ x, y, z })
      //   0 // ms transition duration
      // );
      // this.graph.camera().position.z = Math.cbrt(this.graph.graphData().nodes.length) * 150;
      // TODO chekc behavior
    },
    updateGeometries() {
      // fn used to update the rendering of the graph
      // set .emitLoadComplete to false avoid the emit of 'loadComplete'
      this.graph.emitLoadComplete = false;
      this.graph.nodeRelSize(4);
    },
    applyHPARNAlevelsOnMap(RNAlevels) {
      this.HPARNAlevels = RNAlevels;
      this.updateGeometries();
      if (Object.keys(this.HPARNAlevels).length !== 0) {
        EventBus.$emit('loadRNAComplete', true, '');
      }
    },
    highlight(elements, className) {
      console.log(elements, className);
    },
    unHighlight(elements, className) {
      console.log(elements, className);
      this.searchIDsSet = new Set();
      this.searchedNodesOnGraph = [];
      this.updateGeometries();
    },
    reformatChemicalReactionHTML,
  },
};
</script>

<style lang="scss">

#graph3D {
 height: 100%;
 width: 100%;
 overflow: hidden;
}

</style>
