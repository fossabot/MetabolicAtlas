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
import { debounce } from 'vue-debounce';
import MapSearch from '@/components/explorer/mapViewer/MapSearch';
import { default as EventBus } from '../../../event-bus';
import { reformatChemicalReactionHTML } from '../../../helpers/utils';

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
      staticSearch: false,

      HPARNAlevels: {},
      defaultGeneColor: '#feb',
      tissue: 'None',
      searchTerm: '',

      listenControl: false,
      disableControlsListener: false,
    };
  },
  watch: {
    graph(v) {
      if (v === null) {
        this.listenControl = false;
      } else if (!this.listenControl) {
        this.listenControl = true;
        v.controls()
          .addEventListener('change', this.updateURLCoord, false);
      }
    },
    '$route': function watchSetup() { // eslint-disable-line quote-props
      this.disableControlsListener = this.$route.name !== 'viewer';
    },
  },
  created() {
    EventBus.$off('show3Dnetwork');
    EventBus.$off('destroy3Dnetwork');
    EventBus.$off('update3DLoadedComponent');
    EventBus.$off('apply3DHPARNAlevels');
    EventBus.$off('recompute3DCanvasBounds');

    EventBus.$on('show3Dnetwork', (type, name, searchTerm, selectIDs, coords) => {
      if (selectIDs && selectIDs.length === 1) {
        this.focusOnID = selectIDs[0]; // eslint-disable-line prefer-destructuring
      } else {
        // do not handle multiple ids for now;
        this.focusOnID = null;
      }
      this.searchTerm = searchTerm;
      this.coords = coords !== '0,0,0,0,0,0' ? coords : null; // FIXME duplicated '0,0,0,0,0,0'
      if (this.loadedComponentType !== type || this.loadedComponentName !== name) {
        this.selectElementID = null;
        this.selectElementIDfull = null;
        this.$refs.mapsearch.reset();
        if (this.graph) {
          this.coords = null;
        }
        this.loadedComponentType = type;
        this.loadedComponentName = name;
        if (name in this.networkHistory) {
          this.$emit('loading');
          this.graph.resetCamera = true;
          this.graph.reloadHistory = true;
          this.network = this.networkHistory[name];
          this.graph.graphData(this.network);
          this.graph.emitLoadComplete = true;
          this.graph.skipLoadComplete = false;
        } else {
          this.getJson();
        }
      } else if (selectIDs.length !== 0 || this.searchTerm) {
        this.updateGeometries();
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

    this.updateURLCoord = debounce(this.updateURLCoord, 150);
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
              this.graph.skipLoadComplete = false;
              this.graph.resetCamera = true;
              this.constructGraph();
            } else {
              this.graph.resetCamera = true;
              this.graph.graphData(this.network);
            }
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
            return 'orange'; // FIXME should be 'border orange' not 'fill orange'
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
          this.updateGraphBounds();
          if (this.selectIDs.length !== 0 && this.selectIDs[0] !== this.selectElementID) {
            this.selectElement(
              this.graph.graphData().nodes.find(
                n => n.id.split('-')[0].toLowerCase() === this.selectIDs[0].toLowerCase()
              )
            );
            this.selectIDs = [];
          }

          if (this.coords) {
            this.moveCameraPosition.apply(
              null, this.coords.split(',').map(v => parseFloat(v)));
            // clear var coords, auto move should be only performed once
            this.coords = null;
            this.staticSearch = true;
          } else if (this.graph.emitLoadComplete) {
            EventBus.$emit('update_url_coord', 0, 0, 0, 0, 0, 0);
          }

          if (this.searchTerm) {
            this.$refs.mapsearch.search(this.searchTerm);
            this.searchTerm = '';
          }

          if (this.graph.resetCamera) {
            this.graph.resetCamera = false;
            this.resetCameraPosition();
          }
          if (this.graph !== null && (this.graph.emitLoadComplete || !this.graph.skipLoadComplete)) {
            // .emitLoadComplete is forced to true when the show3D map is called
            // .skipLoadComplete is set to true when the graph should be just re-rendered
            this.$emit('loadComplete', true, '');
            this.graph.emitLoadComplete = false;
          } else {
            this.graph.skipLoadComplete = false;
          }
        });
    },
    updateGraphBounds() {
      setTimeout(() => {
        if (this.$refs.graphParent && this.$refs.graphParent.offsetParent) {
          const width = this.$refs.graphParent.offsetParent.offsetWidth;
          const height = this.$refs.graphParent.offsetParent.offsetHeight;
          if (this.graph.width() !== width || this.graph.height() !== height) {
            this.graph.width(width).height(height);
          }
        }
      }, 0);
    },
    updateURLCoord(ev) {
      if (this.disableControlsListener) {
        this.disableControlsListener = false;
        return;
      }
      const pos = ev.target.object.position; // eslint-disable-line no-unused-vars
      const { lookAt } = this.graph.cameraPosition(); // eslint-disable-line no-unused-vars
      // FIXME invalid coor, lookAt seems correct but the camera rotation point is not
      EventBus.$emit('update_url_coord', pos.x, pos.y, pos.z, lookAt.x, lookAt.y, lookAt.z);
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
      this.searchIDsSet = new Set(ids);
      this.searchedNodesOnGraph = this.graph.graphData().nodes.filter(n => this.searchIDsSet.has(n.id.split('-')[0]));
      if (!this.staticSearch && this.searchedNodesOnGraph.length !== 0) {
        this.focusOnNode(this.searchedNodesOnGraph[0]);
      }
      this.staticSearch = false;
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
    moveCameraPosition(x, y, z, lx, ly, lz) { // eslint-disable-line no-unused-vars
      this.disableControlsListener = true;
      this.graph.cameraPosition(
        { x, y, z },
        { x: lx, y: ly, z: lz }, // lookAt ({ x, y, z })
        0 // ms transition duration
      );
    },
    resetCameraPosition() {
      this.moveCameraPosition(0, 0, Math.cbrt(this.graph.graphData().nodes.length) * 150);
    },
    updateGeometries() {
      // function to (fast?) re-render the graph
      // set .skipLoadComplete to true avoid the emit of 'loadComplete'
      // but works only if .emitLoadComplete is set to false
      this.graph.skipLoadComplete = true;
      this.graph.nodeRelSize(4);
    },
    applyHPARNAlevelsOnMap(RNAlevels) {
      this.HPARNAlevels = RNAlevels;
      this.updateGeometries();
      if (Object.keys(this.HPARNAlevels).length !== 0) {
        EventBus.$emit('loadRNAComplete', true, '');
      }
    },
    unHighlight() {
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
