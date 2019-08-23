<template>
  <div ref="graphParent">
    <div id="graph3D"></div>
  </div>
</template>

<script>

import axios from 'axios';
import forceGraph3D from '3d-force-graph';
import { default as EventBus } from '../../../event-bus';
import { getExpressionColor } from '../../../expression-sources/hpa';
import { reformatChemicalReactionHTML } from '../../../helpers/utils';

export default {
  name: 'd3dforce',
  props: [
    'model',
  ],
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
      geneRNAlevels: {},
      HPARNAlevelsHistory: {},
      defaultGeneColor: '#feb',
      tissue: 'None',
      focusOnID: null,
    };
  },
  created() {
    EventBus.$off('show3Dnetwork');
    EventBus.$off('destroy3Dnetwork');
    EventBus.$off('update3DLoadedComponent');
    EventBus.$off('load3DHPARNAlevels');

    EventBus.$on('show3Dnetwork', (type, name, ids) => {
      if (name.toLowerCase().substr(0, 7) === 'cytosol') {
        name = 'cytosol'; // eslint-disable-line no-param-reassign
      }
      if (ids && ids.length === 1) {
        this.focusOnID = ids[0];
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

    EventBus.$on('load3DHPARNAlevels', (mapType, tissue) => {
      this.loadHPAlevelsOnMap(mapType, tissue);
    });
  },
  methods: {
    getJson() {
      this.$emit('loading');
      this.tissue = 'None';
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
            if (this.tissue === 'None') {
              return this.defaultGeneColor;
            }
            const partialID = n.id.split('-')[0];
            if (this.geneRNAlevels[partialID] !== undefined) {
              return getExpressionColor(this.geneRNAlevels[partialID]);
            }
            return 'whitesmoke';
          } else if (n.g === 'r') {
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
          if (this.graph !== null &&
            this.graph.emitLoadComplete !== undefined &&
            !this.graph.emitLoadComplete) {
            this.graph.emitLoadComplete = true;
          } else if (this.graph.graphData().nodes.length !== 0) {
            this.$emit('loadComplete', true, '');
          }
          if (this.focusOnID) {
            this.focusOnNode(this.focusOnID);
          }
        });
    },
    updateGraphBounds() {
      setTimeout(() => {
        if (this.$refs.graphParent.offsetParent) {
          const width = this.$refs.graphParent.offsetParent.offsetWidth; // FIXME
          const height = this.$refs.graphParent.offsetParent.offsetHeight; // FIXME
          if (this.graph.width() !== width || this.graph.height() !== height) {
            this.graph.width(width).height(height);
          }
        }
      }, 0);
    },
    getElementIdAndType(element) {
      if (element.g === 'r') {
        return [element.id, 'reaction'];
      } else if (element.g === 'e') {
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
          let data = response.data;
          if (type === 'reaction') {
            data = data.reaction;
            data.equation = this.reformatChemicalReactionHTML(data, true);
          } else if (type === 'gene') {
            // add the RNA level if any
            if (id in this.geneRNAlevels) {
              data.rnaLvl = this.geneRNAlevels[id];
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
      node = node[0];
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
          3000, // ms transition duration
        );
      }, 0);
    },
    resetCameraPosition() {
      this.graph.cameraPosition(
        { x: 0, y: 0, z: 0 },
        { x: 0, y: 0, z: 0 }, // lookAt ({ x, y, z })
        0, // ms transition duration
      );
      this.graph.camera().position.z = Math.cbrt(this.graph.graphData().nodes.length) * 150;
    },
    updateGeometries(emitLoadComplete) {
      this.graph.emitLoadComplete = emitLoadComplete;
      this.graph.nodeRelSize(4);
    },
    loadHPAlevelsOnMap(mapType, tissue) {
      if (this.loadedComponentName in this.HPARNAlevelsHistory) {
        this.tissue = tissue;
        this.readHPARNAlevels(tissue);
        return;
      }
      axios.get(`${this.model.database_name}/gene/hpa_rna_levels/${mapType}/3d/${this.loadedComponentName}`)
        .then((response) => {
          this.HPARNAlevelsHistory[this.loadedComponentName] = response.data;
          this.tissue = tissue;
          setTimeout(() => {
            this.readHPARNAlevels(tissue);
          }, 0);
        })
        .catch(() => {
          EventBus.$emit('loadRNAComplete', false, '');
        });
    },
    readHPARNAlevels(tissue) {
      if (tissue === 'None') {
        this.geneRNAlevels = {};
        this.updateGeometries(false);
        return;
      }
      const index = this.HPARNAlevelsHistory[this.loadedComponentName].tissues.indexOf(tissue);
      if (index === -1) {
        EventBus.$emit('loadRNAComplete', false, '');
        return;
      }

      const levels = this.HPARNAlevelsHistory[this.loadedComponentName].levels;
      for (const array of levels) {
        const enzID = array[0];
        let level = Math.log2(parseFloat(array[1].split(',')[index]) + 1);
        level = Math.round((level + 0.00001) * 100) / 100;
        this.geneRNAlevels[enzID] = level;
      }

      // update cached selected elements
      for (const id of Object.keys(this.selectedItemHistory)) {
        if (this.geneRNAlevels[id] !== undefined) {
          this.selectedItemHistory[id].rnaLvl = this.geneRNAlevels[id];
        }
      }
      this.updateGeometries(false);
      EventBus.$emit('loadRNAComplete', true, '');
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
