<template>
  <div class="fixed-height">
    <div id="graph3D" :class="{ 'margin-fix' : isMobileWidth() }"></div>
    <div class="canvasOption overlay">
      <span class="button" title="Download as PNG" @click="downloadPNG()"><i class="fa fa-download"></i></span>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import forceGraph3D from '3d-force-graph';
import { default as FileSaver } from 'file-saver';
import { default as EventBus } from '../../../event-bus';
import { reformatChemicalReactionHTML, isMobileWidth } from '@/helpers/utils';

export default {
  name: 'D3dforce',
  props: {
    model: Object,
  },
  data() {
    return {
      errorMessage: '',
      loadedComponentType: null,
      loadedComponentName: null,
      graph: null,
      emptyNetwork: true,
      networkHistory: {},
      network: {
        nodes: [],
        links: [],
      },

      selectedItemHistory: {},
      selectElementID: null,
      selectElementIDfull: null,
      HPARNAlevels: {},
      defaultGeneColor: '#feb',
      tissue: 'None',
      focusOnID: null,
    };
  },
  created() {
    EventBus.$off('show3Dnetwork');
    EventBus.$off('destroy3Dnetwork');
    EventBus.$off('update3DLoadedComponent');
    EventBus.$off('apply3DHPARNAlevels');

    EventBus.$on('show3Dnetwork', (type, name, ids) => {
      if (name.toLowerCase().substr(0, 7) === 'cytosol') {
        name = 'cytosol'; // eslint-disable-line no-param-reassign
      }
      if (ids && ids.length === 1) {
        this.focusOnID = ids[0]; // eslint-disable-line prefer-destructuring
      } else {
        // do not handle multiple ids for now;
        this.focusOnID = null;
      }
      if (this.loadedComponentType !== type
          || this.loadedComponentName !== name
          || this.emptyNetwork) {
        if (!this.emptyNetwork) {
          this.unSelectElement();
        }
        this.loadedComponentType = type;
        this.loadedComponentName = name;
        if (name in this.networkHistory) {
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
        this.focusOnNode(this.focusOnID);
      } else {
        this.$emit('loadComplete', true, '');
      }
    });

    EventBus.$on('destroy3Dnetwork', () => {
      if (this.graph) {
        // this.graph.resetProps();
        // this.graph.null;
        this.graph.graphData({ nodes: [], links: [] });
        this.emptyNetwork = true;
      }
    });

    EventBus.$on('update3DLoadedComponent', (type, name) => {
      this.loadedComponentType = type;
      this.loadedComponentName = name;
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
            this.emptyNetwork = false;
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
          if (n.id === this.selectElementIDfull) {
            return 'red';
          }
          if (n.g === 'e') {
            if (Object.keys(this.HPARNAlevels).length === 0) {
              return this.defaultGeneColor;
            }
            const partialID = n.id.split('-')[0];
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
          if (this.graph !== null
            && this.graph.emitLoadComplete !== undefined
            && !this.graph.emitLoadComplete) {
            this.graph.emitLoadComplete = true;
          } else if (this.graph.graphData().nodes.length !== 0) {
            this.$emit('loadComplete', true, '');
          }
          if (this.focusOnID) {
            this.focusOnNode(this.focusOnID);
          }
        });
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
    getElementIdAndType(element) {
      if (element.g === 'r') {
        return [element.id, 'reaction'];
      } if (element.g === 'e') {
        return [element.id.split('-')[0], 'gene'];
      }
      return [element.id.split('-')[0], 'metabolite'];
    },
    selectElement(element) {
      const [id, type] = this.getElementIdAndType(element);
      if (this.selectElementID === id) {
        this.unSelectElement();
        this.updateGeometries(false);
        return;
      }
      const selectionData = { type, data: null, error: false };
      this.selectElementID = id;
      this.selectElementIDfull = element.id;

      if (this.selectedItemHistory[id]) {
        selectionData.data = this.selectedItemHistory[id];
        this.updateGeometries(false);
        EventBus.$emit('updatePanelSelectionData', selectionData);
        return;
      }

      EventBus.$emit('startSelectedElement');
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
          EventBus.$emit('updatePanelSelectionData', selectionData);
          this.selectedItemHistory[id] = selectionData.data;
          EventBus.$emit('endSelectedElement', true);
          this.updateGeometries(false);
        })
        .catch(() => {
          EventBus.$emit('endSelectedElement', false);
        });
    },
    unSelectElement() {
      this.selectElementID = null;
      this.selectElementIDfull = null;
      EventBus.$emit('unSelectedElement');
    },
    focusOnNode(id) {
      this.focusOnID = null;
      this.unSelectElement();
      let node = this.network.nodes.filter(n => n.g === 'r' && n.id.toLowerCase() === id.toLowerCase());
      if (node.length !== 1) {
        return;
      }
      node = node[0]; // eslint-disable-line prefer-destructuring
      this.selectElement(node, false);
      const np = node.__threeObj.position; // eslint-disable-line no-underscore-dangle
      setTimeout(() => {
        const distance = 120;
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
    resetCameraPosition() {
      this.graph.cameraPosition(
        { x: 0, y: 0, z: 0 },
        { x: 0, y: 0, z: 0 }, // lookAt ({ x, y, z })
        0 // ms transition duration
      );
      this.graph.camera().position.z = Math.cbrt(this.graph.graphData().nodes.length) * 150;
    },
    updateGeometries(emitLoadComplete) {
      this.graph.emitLoadComplete = emitLoadComplete;
      this.graph.nodeRelSize(4);
    },
    applyHPARNAlevelsOnMap(RNAlevels) {
      this.HPARNAlevels = RNAlevels;
      this.updateGeometries(false);
      if (Object.keys(this.HPARNAlevels).length !== 0) {
        EventBus.$emit('loadRNAComplete', true, '');
      }
    },
    reformatChemicalReactionHTML,
    isMobileWidth,
  },
};
</script>

<style lang="scss">

#graph3D {
  max-height: 100%;
  max-width: 100%;
  overflow: hidden;

  &.margin-fix {
    margin-left: 10px;
  }
}

</style>
