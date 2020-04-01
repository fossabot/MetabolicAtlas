<template>
  <div class="interaction-partners">
    <div v-if="!mainNodeID" class="columns">
      <div class="column container has-text-centered">
        <h3 class="title is-3">Explore {{ model.short_name }} with the {{ messages.interPartName }}</h3>
        <h5 class="subtitle is-5 has-text-weight-normal">
          use the search field to find the component of interest
        </h5>
      </div>
    </div>
    <div class="columns is-centered">
      <gem-search ref="gemSearch" :metabolites-and-genes-only="true"></gem-search>
    </div>
    <br><br>
    <div v-if="!mainNodeID">
      <div class="columns is-centered has-text-centered">
        <p class="is-capitalized subtitle is-size-3 has-text-weight-light has-text-grey-light">
          Demo
        </p>
      </div>
      <div class="columns is-centered has-text-justified">
        <div class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
          <!-- eslint-disable max-len -->
          <p>For a given metabolite or gene, this page shows the other metabolites and genes with which it is connected via reactions. For more, see the <router-link :to="{ name: 'documentation', hash: '#Interaction-Partners' }">documentation on {{ messages.interPartName }}</router-link>.
          </p>
          <br>
          <video poster="@/assets/interPart-cover.jpg" playsinline controls muted loop>
            <source src="@/assets/interPart.mp4" type="video/mp4">
          </video>
          <br><br>
        </div>
      </div>
    </div>
    <template v-if="componentNotFound">
      <div class="columns is-centered">
        <notFound type="Interaction Partners" :component-id="mainNodeID"></notFound>
      </div>
    </template>
    <template v-if="loading">
      <loader></loader>
    </template>
    <template v-else-if="mainNodeID && !componentNotFound">
      <div class="container columns">
        <div class="column is-8">
          <h3 class="title is-3 is-marginless" v-html="`${messages.interPartName} for ${title}`"></h3>
        </div>
      </div>
      <div v-show="showGraphContextMenu && showNetworkGraph" id="contextMenuGraph" ref="contextMenuGraph">
        <span v-show="clickedElmId && clickedElmId !== mainNodeID"
              class="button is-dark" @click="navigate">Load {{ messages.interPartName }}</span>
        <span v-show="clickedElmId && !expandedIds.includes(clickedElmId)"
              class="button is-dark" @click="loadExpansion">Expand {{ messages.interPartName }}</span>
        <div v-show="clickedElm">
          <span class="button is-dark">Highlight reaction:</span>
        </div>
        <div>
          <template v-if="clickedElm && clickedElm['reaction']">
            <template v-for="(r, index) in Array.from(clickedElm.reaction).slice(0,16)">
              <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
              <span v-if="index != 15" class="button is-dark is-small has-margin-left"
                    @click="highlightReaction(r)">
                {{ r }}
              </span>
              <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
              <span v-else class="has-margin-left">
                {{ `${Array.from(clickedElm.reaction).length - 15} others reaction(s)...` }}
              </span>
            </template>
          </template>
        </div>
      </div>
      <div class="container columns is-multiline">
        <template v-if="tooLargeNetworkGraph">
          <div class="column is-8-desktop is-fullwidth-tablet">
            <div class="notification is-warning has-text-centered">
              The query has returned many nodes.
              <br>
              The network cannot been generated.
            </div>
          </div>
        </template>
        <template v-if="largeNetworkGraph">
          <div class="column is-8-desktop is-fullwidth-tablet">
            <div class="notification is-warning has-text-centered">
              <div>
                The query has returned many nodes.
                <br>
                The network has not been generated.
              </div>
              <span class="button" @click="generateGraph(fitGraph)">Generate</span>
            </div>
          </div>
        </template>
        <template v-else-if="showNetworkGraph">
          <div class="column is-8-desktop is-fullwidth-tablet">
            <div id="graphOption">
              <span class="button" :class="[{ 'is-active': showGraphLegend }, '']"
                    title="Options" @click="toggleGraphLegend"><i class="fa fa-cog"></i></span>
              <span class="button" title="Zoom In" @click="zoomGraph(true)"><i class="fa fa-search-plus"></i></span>
              <span class="button" title="Zoom Out" @click="zoomGraph(false)">
                <i class="fa fa-search-minus"></i>
              </span>
              <span class="button" title="Fit to frame" @click="fitGraph()"><i class="fa fa-arrows-alt"></i></span>
              <span class="button" title="Reload" @click="resetGraph(true)"><i class="fa fa-refresh"></i></span>
              <span class="button" title="Clean selection/highlight" @click="resetGraph(false)">
                <i class="fa fa-eraser"></i>
              </span>
            </div>
            <div v-show="showGraphLegend" id="contextGraphLegend" ref="contextGraphLegend">
              <button class="delete" @click="toggleGraphLegend"></button>
              <span class="label">Gene</span>
              <div class="comp">
                <span>Shape:</span>
                <div class="select">
                  <select v-model="nodeDisplayParams.geneNodeShape" @change="redrawGraph()">
                    <option v-for="shape in availableNodeShape" :key="shape">
                      {{ shape }}
                    </option>
                  </select>
                </div>
                <span>Color:</span>
                <span class="color-span clickable"
                      :style="{ background: nodeDisplayParams.geneNodeColor.hex }"
                      @click="toggleGeneColorPicker()">
                  <compact-picker v-show="showColorPickerEnz"
                                  v-model="nodeDisplayParams.geneNodeColor"
                                  @input="updateExpAndredrawGraph(false, 'gene')">
                  </compact-picker>
                </span>
              </div>
              <br>
              <span class="label">Metabolite</span>
              <div class="comp">
                <span>Shape:</span>
                <div class="select">
                  <select v-model="nodeDisplayParams.metaboliteNodeShape"
                          @change="redrawGraph()">
                    <option v-for="shape in availableNodeShape" :key="shape">
                      {{ shape }}
                    </option>
                  </select>
                </div>
                <span>Color:</span>
                <span class="color-span clickable"
                      :style="{ background: nodeDisplayParams.metaboliteNodeColor.hex }"
                      @click="toggleMetaboliteColorPicker()">
                  <compact-picker v-show="showColorPickerMeta"
                                  v-model="nodeDisplayParams.metaboliteNodeColor"
                                  @input="updateExpAndredrawGraph(false, 'metabolite')">
                  </compact-picker>
                </span>
              </div>
            </div>
            <div id="cy" ref="cy" class="card is-paddingless">
            </div>
          </div>
        </template>
        <div class="column">
          <template v-if="showNetworkGraph">
            <div id="dropdownMenuExport" class="dropdown">
              <div class="dropdown-trigger">
                <a v-show="showNetworkGraph" class="button is-primary is-outlined" aria-haspopup="true"
                   aria-controls="dropdown-menu" @click="showMenuExport=!showMenuExport">
                  <span class="icon is-large"><i class="fa fa-download"></i></span>
                  <span>Export graph</span>
                  <span class="icon is-large"><i class="fa fa-caret-down"></i></span>
                </a>
              </div>
              <div v-show="showMenuExport" id="dropdown-menu"
                   class="dropdown-menu" role="menu"
                   @mouseleave="showMenuExport = false">
                <div class="dropdown-content">
                  <a class="dropdown-item" @click="exportGraphml">
                    Graphml
                  </a>
                  <a class="dropdown-item" @click="exportPNG">
                    PNG
                  </a>
                </div>
              </div>
            </div>
            <br><br>
            <div class="card ">
              <header class="card-header">
                <p class="card-header-title">
                  <label class="checkbox is-unselectable"
                         :title="disableExpLvl ? 'Expression levels are not available' : `Click to ${toggleGeneExpLevel ? 'disable' : 'activate'} expression RNA levels`"> <!-- eslint-disable-line max-len -->
                    <input v-model="toggleGeneExpLevel" type="checkbox"
                           :disabled="disableExpLvl"
                           @click="applyLevels('gene', 'HPA', 'RNA', selectedSample)">
                    Enable <a href="https://www.proteinatlas.org/" target="_blank">proteinAtlas.org</a>&nbsp;RNA levels
                  </label>
                </p>
              </header>
              <div v-show="toggleGeneExpLevel" class="card-content card-content-compact">
                <RNALegend></RNALegend>
                <br>
                <div v-show="toggleGeneExpLevel && !disableExpLvl"
                     class="select is-fullwidth"
                     :class="{ 'is-loading' : loadingHPA && toggleGeneExpLevel}">
                  <select id="enz-select" ref="enzHPAselect"
                          v-if="tissues.HPA" v-model="selectedSample" :disabled="!toggleGeneExpLevel"
                          title="Select a tissue type"
                          @change.prevent="applyLevels('gene', 'HPA', 'RNA', selectedSample)">
                    <optgroup label="HPA - RNA levels - Tissues">
                      <!--  <option value="None">None</option> -->
                      <option v-for="tissue in tissues['HPA']" :key="tissue" :value="tissue">
                        {{ tissue }}
                      </option>
                    </optgroup>
                    <optgroup v-if="false" label="HPA - RNA levels - Cell-type">
                      <option v-for="cellType in cellLines['HPA']" :key="cellType" :value="cellType">
                        {{ cellType }}
                      </option>
                    </optgroup>
                  </select>
                </div>
              </div>
            </div>
            <br>
            <div v-if="compartmentList.length !== 0 || subsystemList.length != 0" class="card">
              <header class="card-header">
                <p class="card-header-title">
                  Highlight
                </p>
              </header>
              <div class="card-content card-content-compact">
                <div class="select is-fullwidth">
                  <select v-model="compartmentHL" :disabled="disableCompartmentHL"
                          @change.prevent="highlightCompartment">
                    <option v-if="!disableCompartmentHL" value="" disabled>Select a compartment</option>
                    <option v-for="compartment in compartmentList"
                            :key="compartment" :value="disableCompartmentHL ? '' : compartment">
                      {{ compartment }}
                    </option>
                  </select>
                </div>
                <div v-show="subsystemList.length !== 0">
                  <br>
                  <div class="select is-fullwidth">
                    <select v-model="subsystemHL" @change.prevent="highlightSubsystem">
                      <option value="" disabled>Select a subsystem</option>
                      <option v-for="sub in subsystemList" :key="sub" :value="sub">
                        {{ sub }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <br>
          </template>
          <sidebar id="sidebar" :selected-elm="clickedElm" :showIPbutton="clickedElmId !== mainNodeID" />
        </div>
      </div>
      <cytoscape-table :reactions="reactions" :selected-elm-id="clickedElmId" :selected-reaction-id="reactionHL"
                       :is-graph-visible="showNetworkGraph"
                       :filename="filename"
                       @highlight="highlightNode($event)" @HLreaction="highlightReaction($event)">
      </cytoscape-table>
    </template>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import cytoscape from 'cytoscape';
import jquery from 'jquery';
import cola from 'cytoscape-cola';
import { Compact } from 'vue-color';
import { default as FileSaver } from 'file-saver';

import GemSearch from '@/components/explorer/gemBrowser/GemSearch';
import Sidebar from '@/components/explorer/interactionPartners/Sidebar';
import CytoscapeTable from '@/components/explorer/interactionPartners/CytoscapeTable';
import Loader from '@/components/Loader';
import RNALegend from '@/components/explorer/mapViewer/RNALegend.vue';
import NotFound from '@/components/NotFound';

import { default as transform } from '@/data-mappers/hmr-closest-interaction-partners';
import { default as graph } from '@/graph-stylers/hmr-closest-interaction-partners';

import { default as convertGraphML } from '@/helpers/graph-ml-converter';

import { getSingleRNAExpressionColor } from '@/expression-sources/hpa';
import { default as messages } from '@/helpers/messages';


export default {
  name: 'InteractionPartners',
  components: {
    NotFound,
    GemSearch,
    Sidebar,
    CytoscapeTable,
    Loader,
    'compact-picker': Compact,
    RNALegend,
  },
  data() {
    return {
      loading: false,
      loadingHPA: false,
      componentNotFound: false,
      errorMessage: '',

      nodeCount: 0,
      warnNodeCount: 50,
      maxNodeCount: 100,
      showNetworkGraph: false,
      largeNetworkGraph: false,

      rawRels: {},
      rawElms: {},

      mainNodeID: '',
      mainNode: null,

      clickedElmId: '',
      clickedElm: null,
      selectedSample: '',

      expandedIds: [],

      cellLines: {},
      legend: '',

      expSource: '',
      expType: '',
      expSample: '',

      reactionHL: null,
      compartmentHL: '',
      compartmentList: [],
      disableCompartmentHL: false,
      subsystemHL: '',
      subsystemList: [],

      // keep track of exp lvl source already loaded
      expSourceLoaded: {
        gene: {},
        metabolite: {},
      },
      disableExpLvl: false,

      cy: null,

      showMenuExport: false,
      showMenuExpression: false,
      toggleGeneExpLevel: false,
      toggleMetaboliteExpLevel: false,

      showGraphLegend: false,
      showGraphContextMenu: false,
      showColorPickerEnz: false,
      showColorPickerMeta: false,

      availableNodeShape: [
        'rectangle',
        'roundrectangle',
        'cutrectangle',
        'ellipse',
        'triangle',
        'pentagon',
        'hexagon',
        'heptagon',
        'octagon',
        'star',
        'diamond',
        'vee',
        'rhomboid',
      ],

      nodeDisplayParams: {
        geneExpSource: false,
        geneExpType: false,
        geneExpSample: false,
        geneNodeShape: 'rectangle',
        geneNodeColor: {
          hex: '#9F0500',
          hsl: {
            h: 1.8868, s: 1, l: 0.3118, a: 1,
          },
          hsv: {
            h: 1.8868, s: 1, v: 0.6235, a: 1,
          },
          rgba: {
            r: 159, g: 5, b: 0, a: 1,
          },
          a: 1,
        },
        metaboliteExpSource: false,
        metaboliteExpType: false,
        metaboliteExpSample: false,
        metaboliteNodeShape: 'ellipse',
        metaboliteNodeColor: {
          hex: '#73D8FF',
          hsl: {
            h: 196.714, s: 1, l: 0.7255, a: 1,
          },
          hsv: {
            h: 196.7142, s: 0.549, v: 1, a: 1,
          },
          rgba: {
            r: 115, g: 216, b: 255, a: 1,
          },
          a: 1,
        },
      },
      maxZoom: 10,
      minZoom: 0.1,
      factorZoom: 0.08,
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      tissues: state => state.humanProteinAtlas.tissues,
      matLevels: state => state.humanProteinAtlas.matLevels,
      tooLargeNetworkGraph: state => state.interactionPartners.tooLargeNetworkGraph,
      expansion: state => state.interactionPartners.expansion,
    }),
    ...mapGetters({
      component: 'interactionPartners/component',
      reactions: 'interactionPartners/reactions',
      title: 'interactionPartners/title',
      reactionSet: 'interactionPartners/reactionsSet',
      componentName: 'interactionPartners/componentName',
    }),
    filename() {
      return `MetAtlas Interaction Partners for ${this.componentName} ${this.mainNodeID}`;
    },
    elms() {
      if (Object.keys(this.rawElms).length !== 0) {
        return Object.keys(this.rawElms).map(k => this.rawElms[k]);
      }
      return [];
    },
    rels() {
      return Object.keys(this.rawRels).map(k => this.rawRels[k]);
    },
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': async function watchSetup() {
      if (this.$route.path.includes('/interaction/')) {
        if (this.mainNodeID !== this.$route.params.id) {
          await this.setup();
        }
      }
    },
  },
  async beforeMount() {
    cytoscape.use(cola);
    jquery(window).resize(() => {
      jquery('#cy').height(jquery('#cy').width() / 1.5);
      this.fitGraph();
    });
    await this.setup();
  },
  methods: {
    async setup() {
      this.mainNodeID = this.$route.params.id;
      this.mainNode = null;
      this.reactionHL = null;
      this.compartmentHL = '';
      this.subsystemHL = '';
      await this.loadHPATissue();
      if (this.mainNodeID) {
        await this.load();
        jquery('#cy').height(jquery('#cy').width() / 1.5);
      }
    },
    navigate() {
      this.reactionHL = null;
      this.compartmentHL = '';
      this.subsystemHL = '';
      this.$router.push({ name: 'interPartner', params: { model: this.model.database_name, id: this.clickedElmId } });
    },
    async loadHPATissue() {
      try {
        await this.$store.dispatch('humanProteinAtlas/getTissues', this.model.database_name);
        if (this.tissues.HPA.length === 0) {
          this.disableExpLvl = true;
        }
      } catch {
        this.disableExpLvl = true;
      }
    },
    async load() {
      this.loading = true;

      try {
        const payload = { model: this.model.database_name, id: this.mainNodeID };
        await this.$store.dispatch('interactionPartners/getInteractionPartners', payload);

        // TODO: consider refactoring the following lines in this try block into Vuex,
        //       as well as duplication with the loadExpansion method
        this.componentNotFound = false;
        this.showGraphContextMenu = false;
        if (this.tooLargeNetworkGraph) {
          this.showNetworkGraph = false;
          return;
        }

        [this.rawElms,
          this.rawRels,
          this.compartmentList,
          this.subsystemList] = transform(this.component, this.reactions, null, null, null, null);
        if (this.compartmentList.length === 1) {
          this.compartmentHL = '';
          this.disableCompartmentHL = true;
        }
        this.mainNode = this.rawElms[this.component.id];
        this.mainNode.name = this.componentName;

        this.expandedIds = [];
        this.expandedIds.push(this.component.id);

        this.nodeCount = Object.keys(this.rawElms).length;
        if (this.nodeCount > this.warnNodeCount) {
          this.showNetworkGraph = false;
          this.largeNetworkGraph = true;
          this.errorMessage = '';
          return;
        }
        this.largeNetworkGraph = false;
        this.showNetworkGraph = true;
        this.errorMessage = '';

        this.resetGeneExpression();

        // The set time out wrapper enforces this happens last.
        setTimeout(() => {
          this.constructGraph(this.rawElms, this.rawRels, this.fitGraph);
        }, 0);
      } catch (error) {
        switch (error.status) {
          case 404:
            this.componentNotFound = true;
            break;
          default:
            this.errorMessage = messages.unknownError;
        }
      } finally {
        this.loading = false;
      }
    },
    async loadExpansion() {
      try {
        const payload = { model: this.model.database_name, id: this.mainNodeID };
        await this.$store.dispatch('interactionPartners/loadExpansion', payload);

        this.reactionHL = null;
        this.errorMessage = null;
        this.showGraphContextMenu = false;

        if (this.tooLargeNetworkGraph) {
          this.showNetworkGraph = false;
          return;
        }

        [this.rawElms, this.rawRels, this.compartmentList, this.subsystemList] = transform(
          this.expansion.component,
          this.expansion.reactions,
          this.rawElms,
          this.rawRels,
          this.compartmentList,
          this.subsystemList
        );

        if (this.compartmentList.length === 1) {
          this.compartmentHL = '';
          this.disableCompartmentHL = true;
        } else {
          this.disableCompartmentHL = false;
        }

        this.expandedIds.push(this.expansion.component.id);

        this.nodeCount = Object.keys(this.rawElms).length;
        if (this.nodeCount > this.warnNodeCount) {
          this.showNetworkGraph = false;
          this.largeNetworkGraph = true;
          this.errorMessage = '';
          return;
        }
        this.showNetworkGraph = true;
        this.errorMessage = '';

        this.resetGeneExpression();

        // The set time out wrapper enforces this happens last.
        setTimeout(() => {
          this.constructGraph(this.rawElms, this.rawRels);
        }, 0);
      } catch (error) {
        switch (error.status) {
          case 404:
            this.errorMessage = messages.notFoundError;
            break;
          default:
            this.errorMessage = messages.unknownError;
        }
      } finally {
        this.loading = false;
      }
    },
    isCompartmentSubsystemHLDisabled() {
      return ((this.compartmentHL === '' && this.subsystemHL === '')
        || (this.compartmentList.length < 2 && this.subsystemList.length === 0));
    },
    highlightReaction(rid) {
      if (this.cy) {
        this.clickedElmId = '';
        this.reactionHL = rid;
        this.clickedElm = { id: rid, type: 'reaction' };
        this.redrawGraph();
        this.showGraphContextMenu = false;
      }
    },
    highlightCompartment() {
      if (this.compartmentHL) {
        this.redrawGraph();
      }
    },
    highlightSubsystem() {
      if (this.subsystemHL) {
        this.redrawGraph();
      }
    },
    toggleGraphLegend() {
      this.showGraphLegend = !this.showGraphLegend;
      this.showColorPickerEnz = false;
      this.showColorPickerMeta = false;
    },
    fixEnzSelectOption() {
      const option = document.getElementById('enz-select')
        .getElementsByTagName('optgroup')[0].childNodes[0];
      if (option) {
        option.selected = 'selected';
        this.nodeDisplayParams.geneExpSample = option.label;
      }
    },
    updateExpAndredrawGraph(usingExpressionLevel, nodeType, expSource, expType, expSample) {
      setTimeout(() => {
        if ((expSource && expType) && !expSample) {
          // fix option selection! because of optgroup?
          if (this.toggleGeneExpLevel) {
            this.fixEnzSelectOption();
          }
        }
        if (!usingExpressionLevel) {
          if ((nodeType === 'gene' && this.toggleGeneExpLevel)
            || (nodeType === 'metabolite' && this.toggleMetaboliteExpLevel)) {
            return;
          }
        }
        this.redrawGraph();
      }, 0);
    },
    resetHighlight() {
      if (this.isCompartmentSubsystemHLDisabled()) {
        return;
      }
      this.compartmentHL = '';
      this.subsystemHL = '';
    },
    async resetGraph(reload) {
      this.reactionHL = null;
      this.mainNode = null;
      this.clickedElm = null;
      this.clickedElmId = '';
      this.showGraphContextMenu = false;
      this.resetGeneExpression();
      this.resetHighlight();
      if (reload) {
        await this.load();
      } else {
        this.redrawGraph();
      }
    },
    redrawGraph() {
      const stylesheet = graph(this.mainNodeID,
        this.rawElms, this.rawRels, this.nodeDisplayParams,
        this.reactionHL, this.compartmentHL, this.subsystemHL)[1];
      const cyzoom = this.cy.zoom();
      const cypan = this.cy.pan();
      this.cy.style(stylesheet);
      this.cy.viewport({
        zoom: cyzoom,
        pan: cypan,
      });
    },
    fitGraph() {
      jquery('#cy').height(jquery('#cy').width() / 1.5);
      setTimeout(() => {
        this.cy.fit(null, 10);
        this.minZoom = this.cy.zoom() / 2.0;
      }, 300);
    },
    highlightNode(elmId) {
      this.showGraphContextMenu = false;
      this.reactionHL = null;
      this.clickedElmId = elmId;
      this.clickedElm = this.rawElms[elmId];

      if (this.showNetworkGraph) {
        this.cy.nodes().deselect();
        const node = this.cy.getElementById(elmId);
        node.json({ selected: true });
        node.trigger('tap');
        this.redrawGraph();
      }
    },
    generateGraph(callback) {
      this.showNetworkGraph = true;
      this.largeNetworkGraph = false;
      this.errorMessage = null;

      this.resetGeneExpression();

      // The set time out wrapper enforces this happens last.
      setTimeout(() => {
        this.constructGraph(this.rawElms, this.rawRels, callback);
      }, 0);
    },
    // this.switchSVG(compartmentID,
    constructGraph: function constructGraph(elms, rels, callback) {
      const [elements, stylesheet] = graph(this.mainNodeID,
        elms, rels, this.nodeDisplayParams, this.reactionHL, this.compartmentHL, this.subsystemHL);

      const colaOptions = {
        animate: true, // whether to show the layout as it's running
        refresh: 0.1, // number of ticks per frame; higher is faster but more jerky
        maxSimulationTime: 10000, // max length in ms to run the layout
        ungrabifyWhileSimulating: false, // so you can't drag nodes during layout
        fit: true, // on every layout reposition of nodes, fit the viewport
        padding: 30, // padding around the simulation
        boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
        nodeDimensionsIncludeLabels: undefined,
        // whether labels should be included in determining the space used
        // by a node (default true)

        // layout event callbacks
        ready() {}, // on layoutready
        stop() {}, // on layoutstop

        // positioning options
        randomize: false, // use random node positions at beginning of layout
        avoidOverlap: true, // if true, prevents overlap of node bounding boxe
        handleDisconnected: true, // if true, avoids disconnected components from overlappin
        nodeSpacing() { return 10; }, // extra spacing around node
        flow: undefined,
        // use DAG/tree flow layout if specified, e.g. { axis: 'y', minSeparation: 30 }
        alignment: undefined,
        // relative alignment constraints on nodes,
        // e.g. function( node ){ return { x: 0, y: 1 } }
        // different methods of specifying edge length
        // each can be a constant numerical value or a function
        // like `function( edge ){ return 2; }
        edgeLength: undefined, // sets edge length directly in simulation
        edgeSymDiffLength: undefined, // symmetric diff edge length in simulation
        edgeJaccardLength: undefined, // jaccard edge length in simulation

        // iterations of cola algorithm; uses default values on undefined
        unconstrIter: undefined, // unconstrained initial layout iterations
        userConstIter: undefined, // initial layout iterations with user-specified constraints
        allConstIter: undefined,
        // initial layout iterations with all constraints including non-overlap

        // infinite layout options
        infinite: false, // overrides all other options for a forces-all-the-time mode
      };
      const { mainNodeID } = this;
      this.cy = cytoscape({
        container: this.$refs.cy,
        elements,
        style: stylesheet,
        layout: {
          // check 'cola' layout extension
          name: Object.keys(elms).length > 30 ? 'concentric' : 'cola',
          colaOptions,
          concentric(node) {
            if (node.degree() === 1) {
              return 1;
            }
            if (node.data().id === mainNodeID) {
              return 10000;
            }
            if (node.data().type === 'gene') {
              return 100;
            }
            return 200;
          },
          ready: this.fitGraph,
        },
      });
      this.cy.userZoomingEnabled(false);

      window.pageYOffset = 0;
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;

      const cyt = this.cy;
      cyt.on('zoom', () => {
        const dim = Math.ceil(10 / cyt.zoom());
        const edgeWidth = 1 / cyt.zoom();

        cyt.$('edge').css({
          width: edgeWidth,
          'font-size': dim / 2,
        });

        cyt.$('node').css({
          width: dim,
          height: dim,
          'font-size': dim * 1.5,
          'text-opacity': 1,
          'overlay-padding': edgeWidth * 2,
        });
      });

      const { contextMenuGraph } = this.$refs;
      this.showGraphContextMenu = false;
      this.showNetworkGraph = true;

      const updateContextMenuPosition = (node) => {
        contextMenuGraph.style.left = `${node.renderedPosition().x + 15}px`;
        contextMenuGraph.style.top = `${node.renderedPosition().y + 160}px`;
      };

      this.cy.on('tap tapstart cxttap', (evt) => {
        if (evt.target === this.cy) {
          this.cy.nodes().deselect();
          this.showGraphContextMenu = false;
          this.clickedElmId = '';
          this.clickedElm = null;
        }
      });

      this.cy.on('tap cxttap', 'node', (evt) => {
        const node = evt.target;
        this.cy.nodes().deselect();
        node.json({ selected: true });
        const elmId = node.data().id;
        this.clickedElmId = elmId;
        this.clickedElm = this.rawElms[elmId];
        updateContextMenuPosition(node);
        this.showGraphContextMenu = evt.type === 'cxttap';
      });

      if (callback) {
        callback();
      }
    },
    exportGraphml: function exportGraphml() {
      const output = convertGraphML(this.cy);
      const blob = new Blob([output], { type: 'text/graphml' });
      const fn = `${this.filename}.graphml`;
      FileSaver.saveAs(blob, fn);
    },
    exportPNG: function exportPNG() {
      const a = document.createElement('a');
      const output = this.cy.png({
        bg: 'white',
      });

      a.href = output;
      a.download = `${this.filename}.png`;
      a.target = '_blank';
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
    async applyLevels(componentType, expSource, expType, expSample) {
      setTimeout(async () => { // wait this.toggleGeneExpLevel
        if (this.disableExpLvl) {
          return;
        }
        this.expSource = expSource;
        this.expType = expType;
        this.expSample = expSample;
        if (componentType === 'gene') {
          if (this.toggleGeneExpLevel) {
            if (this.nodeDisplayParams.geneExpSource !== expSource) {
              this.nodeDisplayParams.geneExpSource = expSource;
              this.nodeDisplayParams.geneExpType = expType;
              // check if this source for ths type of component have been already loaded
              if (!Object.keys(this.expSourceLoaded[componentType]).length === 0
                || !this.expSourceLoaded[componentType][expSource]) {
                // sources that load all exp type
                if (expSource === 'HPA') {
                  await this.getHPAexpression(this.rawElms, expSample);
                } else {
                  // load expression data from another source here
                }
              } else {
                this.updateExpAndredrawGraph(true, componentType, expSource, expType, expSample);
              }
            } else if (this.nodeDisplayParams.geneExpType !== expType) {
              this.nodeDisplayParams.geneExpType = expType;
              if (!this.expSourceLoaded.componentType.expSource.expType) {
                // sources that load only one specific exp type
                this.updateExpAndredrawGraph(true, componentType, expSource, expType, expSample);
              }
            } else if (this.nodeDisplayParams.geneExpSample !== expSample) {
              this.updateExpAndredrawGraph(true, componentType, expSource, expType, expSample);
            }
            this.nodeDisplayParams.geneExpSample = expSample;
          } else {
            // disable expression lvl for gene
            this.nodeDisplayParams.geneExpSource = false;
            this.nodeDisplayParams.geneExpType = false;
            this.nodeDisplayParams.geneExpSample = false;
            this.updateExpAndredrawGraph(true, componentType, expSource, expType, expSample);
          }
        } else if (this.toggleMetaboliteExpLevel) {
          // load data for metabolite
        } else {
          // disable lvl for metabolite
          this.nodeDisplayParams.metaboliteExpSource = false;
          this.nodeDisplayParams.metaboliteExpType = false;
          this.nodeDisplayParams.metaboliteExpSample = false;
        }
      }, 0);
    },
    zoomGraph: function zoomGraph(zoomIn) {
      let factor = this.factorZoom;
      if (!zoomIn) {
        factor = -factor;
      }

      const zoom = this.cy.zoom();
      let lvl = zoom + (zoom * factor);

      if (lvl < this.minZoom) {
        lvl = this.minZoom;
      }

      if (lvl > this.maxZoom) {
        lvl = this.maxZoom;
      }

      if ((lvl === this.maxZoom && zoom === this.maxZoom)
        || (lvl === this.minZoom && zoom === this.minZoom)) {
        return;
      }

      this.cy.zoom({
        level: lvl,
      });
    },
    scrollTo(id) {
      const container = jquery('body, html');
      container.scrollTop(
        jquery(`#${id}`).offset().top - (container.offset().top + container.scrollTop())
      );
    },
    resetGeneExpression() {
      this.toggleGeneExpLevel = false;
      this.nodeDisplayParams.geneExpSource = false;
      this.nodeDisplayParams.geneExpType = false;
      this.nodeDisplayParams.geneExpSample = false;
      this.expSourceLoaded.gene = {};
    },
    async getHPAexpression(rawElms) {
      this.loadingHPA = true;
      const genes = Object.keys(rawElms).filter(el => rawElms[el].type === 'gene');
      const geneIds = genes.map(k => rawElms[k].id);

      try {
        const payload = { model: this.model.database_name, geneIds };
        await this.$store.dispatch('humanProteinAtlas/getMatLevels', payload);

        for (let i = 0; i < this.matLevels.length; i += 1) {
          const array = this.matLevels[i];
          const enzID = array[0];

          if (!(enzID in this.rawElms)) {
            continue; // eslint-disable-line no-continue
          }

          if (!this.rawElms[enzID].expressionLvl) {
            this.rawElms[enzID].expressionLvl = {};
          }
          if (!this.rawElms[enzID].expressionLvl.HPA) {
            this.rawElms[enzID].expressionLvl.HPA = {};
          }
          if (!this.rawElms[enzID].expressionLvl.HPA.RNA) {
            this.rawElms[enzID].expressionLvl.HPA.RNA = {};
          }

          for (let j = 0; j < this.tissues.HPA.length; j += 1) {
            const tissue = this.tissues.HPA[j];
            let level = Math.log2(parseFloat(array[1].split(',')[j]) + 1);
            level = Math.round((level + 0.00001) * 100) / 100;
            this.rawElms[enzID].expressionLvl.HPA.RNA[tissue] = getSingleRNAExpressionColor(level);
          }
        }
        this.expSourceLoaded.gene.HPA = {};
        this.expSourceLoaded.gene.HPA.RNA = true;
        this.disableExpLvl = false;
        this.loadingHPA = false;
        setTimeout(() => {
        // if ((expSource && expType) && !expSample) {
          // fix option selection! because of optgroup?
          // if (this.toggleGeneExpLevel) {
          this.fixEnzSelectOption();
          // }
          //  }
          this.redrawGraph(true);
        }, 0);
      } catch {
        this.loadingHPA = false;
        this.toggleGeneExpLevel = false;
        this.disableExpLvl = true;
        this.nodeDisplayParams.geneExpSource = false;
        this.nodeDisplayParams.geneExpType = false;
        this.nodeDisplayParams.geneExpSample = false;
      }
    },
    toggleGeneColorPicker() {
      this.showColorPickerMeta = false;
      this.showColorPickerEnz = !this.showColorPickerEnz;
      return this.showColorPickerEnz;
    },
    toggleMetaboliteColorPicker() {
      this.showColorPickerEnz = false;
      this.showColorPickerMeta = !this.showColorPickerMeta;
      return this.showColorPickerMeta;
    },
  },
};
</script>

<style lang='scss'>
.interaction-partners {

  h1, h2 {
    font-weight: normal;
  }

  #cy {
    margin: auto;
    width: 100%;
    height: 100%;
  }

  #sidebar {
    max-height: 620px;
    overflow-y: auto;
  }

  #dropdownMenuExport {
    .dropdown-menu {
      display: block;
    }
  }

  #contextMenuGraph, #contextMenuExport, #contextMenuExpression {
    position: absolute;
    z-index: 20;

    span {
      display: block;
      padding: 5px 10px;
      text-align: left;
      border-radius: 0;
      a {
        color: white;
      }
    }

    span.sep.is-black {
      background: #363636;
      border-bottom: 1px solid black;
      height: 1px;
    }
  }

  #errorExpBar {
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 11;
  }

  #graphOption {
    position: absolute;
    top: 12px;
    left: 12px;
    height: 30px;
    z-index: 10;

    span {
      display: inline-block;
      margin-right: 5px;
    }

    select {
      padding: 3px;
    }
  }

  #contextGraphLegend {
    position: absolute;
    background: white;
    top: 44px;
    left: 12px;
    width: auto;
    height: auto;
    padding: 15px;
    border: 1px solid black;
    border-radius: 2px;
    z-index: 30;

    span, div.select, compact-picker {
      display: inline-block;
      margin-right: 20px;
      margin-bottom: 10px;
    }

    div.comp {
      margin-left: 20px;
      display: block;
    }

    span.label {
      display: block;
      margin-left: 0;
    }

    .delete {
      position : absolute;
      right: 10px;
      top: 10px;
    }

    span.color-span {
      height: 20px;
      width: 25px;
      border: 1px solid black;
      vertical-align: middle;
      margin-right: 15px;
      margin-bottom: 5px;
    }
  }

  #t-select {
    margin-top: 0.75rem;
  }

  #enz-select {
    min-width: 240px;
  }

  .slide-fade-enter-active {
    transition: all .3s ease;
  }
  .slide-fade-leave-active {
    transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
  }
  .slide-fade-enter, .slide-fade-leave-active {
    transform: translateX(200px);
    opacity: 0;
  }
}

</style>
