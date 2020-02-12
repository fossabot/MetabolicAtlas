<template>
  <div id="mapViewer" class="extended-section">
    <div id="iMainPanel" class="columns ordered-mobile">
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
        <div id="iSideBar" class="column is-one-fifth-widescreen is-one-quarter-desktop
        is-one-quarter-tablet has-background-lightgray om-2"
             :class=" isMobilePage() ? '' : 'fixed-height scroll' ">
          <div>

            <span id="menuButtons">
              <button class="button is-whitesmoke is-rounded has-text-weight-bold"
                      :disabled="!activeSwitch"
                      :title="activeSwitch ? `Reload the current network in ${ show2D ? '3D' : '2D' }` : ''"
                      @click="switchDimension">
                <template v-if="activeSwitch">
                  Switch to {{ show2D ? '3D' : '2D' }}
                </template>
                <template v-else>
                  <template v-if="!disabled2D">
                    Switch to {{ show2D ? '3D' : '2D' }}
                  </template>
                  <template v-else>
                    Not available in 2D
                  </template>
                </template>
              </button>
              <button class="button is-whitesmoke is-rounded has-text-weight-bold"
                      @click="mapListIsVisible = !mapListIsVisible">
                {{ mapListIsVisible ? 'Hide' : 'Show' }} map list
              </button>
            </span>

            <sidebar-data-panels :model="model" :dim="dim"
                                 :map-type="currentDisplayedType" :map-name="currentDisplayedName"
                                 :maps-data="show2D ? mapsData2D : mapsData3D"
                                 :selection-data="selectionData" :loading="showSelectionLoader">
            </sidebar-data-panels>

            <div v-if="mapListIsVisible" class="card card-margin">
              <div class="has-text-centered">
                <button class="button is-whitesmoke is-rounded has-text-weight-bold card-margin" @click="showMap()">
                  Clear map selection
                </button>
              </div>
              <div class="card-content card-content-compact">
                <ul>
                  <p :title="`Select a ${dim.toUpperCase()} compartment network to show`"></p>
                  <p class="has-text-weight-bold">Compartments:</p>
                  <ul>
                    <div v-if="!has2DCompartmentMaps || show3D">
                      <p v-for="cKey in Object.keys(mapsData3D.compartments).sort()" :key="cKey"
                         :class="{'has-text-weight-bold': cKey === currentDisplayedName }"
                         @click="showMap(mapsData3D.compartments[cKey].id)">
                        <a>{{ mapsData3D.compartments[cKey].name }}
                           {{ mapsData3D.compartments[cKey].reaction_count != 0 ?
                           `(${mapsData3D.compartments[cKey].reaction_count})` : '' }}
                        </a>
                      </p>
                    </div>
                    <div v-else>
                      <p v-for="cKey in Object.keys(mapsData2D.compartments).sort()" :key="cKey"
                         :class="{ 'has-text-whitesmoke' : !mapsData2D.compartments[cKey].sha,
                                   'has-text-weight-bold': cKey === currentDisplayedName }"
                         @click="showMap(mapsData2D.compartments[cKey].id)">
                        <a>{{ mapsData2D.compartments[cKey].name }}
                           {{ mapsData2D.compartments[cKey].reaction_count != 0 ?
                           `(${mapsData2D.compartments[cKey].reaction_count})` : '' }}
                        </a>
                      </p>
                    </div>
                  </ul>
                  <p :title="`Select a ${dim.toUpperCase()} subsystem network to show`"></p><br>
                  <p class="has-text-weight-bold">Subsystems:</p>
                  <ul>
                    <div v-if="!has2DSubsystemMaps || show3D">
                      <p v-for="sKey in Object.keys(mapsData3D.subsystems).sort()" :key="sKey"
                          :class="{'has-text-weight-bold': sKey === currentDisplayedName }"
                          @click="showMap(mapsData3D.subsystems[sKey].id, 'subsystem')">
                        <a>{{ mapsData3D.subsystems[sKey].name }}
                           {{ mapsData3D.subsystems[sKey].reaction_count != 0 ?
                           `(${mapsData3D.subsystems[sKey].reaction_count})` : '' }}
                        </a>
                      </p>
                    </div>
                    <div v-else>
                      <template v-for="sKey in Object.keys(mapsData2D.subsystems).sort()">
                        <template v-if="mapsData2D.subsystems[sKey].id && mapsData2D.subsystems[sKey].sha">
                          <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                          <p :class="{'has-text-weight-bold': sKey === currentDisplayedName }"
                             @click="showMap(mapsData2D.subsystems[sKey].id, 'subsystem')">
                            <a>{{ mapsData2D.subsystems[sKey].name }}
                               {{ mapsData2D.subsystems[sKey].reaction_count != 0 ?
                               `(${mapsData2D.subsystems[sKey].reaction_count})` : '' }}
                            </a>
                          </p>
                        </template>
                        <template v-else>
                          <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                          <p class="disable">
                            {{ mapsData2D.subsystems[sKey].name }}
                          </p>
                        </template>
                      </template>
                    </div>
                  </ul>
                </ul>
              </div>
            </div>

          </div>
        </div>
        <div v-show="showOverviewScreen" class="column fixed-height mapframe om-1">
          <p class="is-size-5 has-text-centered" style="padding: 10%;">
            <a @click="mapListIsVisible = true">Show the map list and choose a compartment or subsystem map</a>
          </p>
        </div>
        <div v-show="!showOverviewScreen" id="graphframe" class="column fixed-height mapframe is-unselectable om-1">
          <svgmap v-show="show2D" :model="model" :maps-data="mapsData2D"
                  @loadComplete="handleLoadComplete" @loading="showLoader=true">
          </svgmap>
          <d3dforce v-show="show3D" :model="model"
                    @loadComplete="handleLoadComplete" @loading="showLoader=true">
          </d3dforce>
          <div v-show="show3D" id="iLoader" class="fixed-height mapframe">
            <a class="button is-loading has-text-white">
              <br>
              <span class="has-text-white is-size-5">Preparing 3D layout</span>
            </a>
          </div>
          <transition name="slide-fade">
            <article v-if="loadErrorMesssage" id="errorBar"
                     class="message"
                     :class="loadErrorTypeMesssage === 'danger' ? 'is-danger' : 'is-info'">
              <div class="message-header">
                <i class="fa"
                   :class="loadErrorTypeMesssage === 'danger' ? 'is-danger' : 'is-info'"></i>
              </div>
              <div class="message-body">
                <h5 class="title is-5">{{ loadErrorMesssage }}</h5>
              </div>
            </article>
          </transition>
        </div>
        <div v-show="!showLoader" id="dataOverlayBar"
             class="column is-narrow has-text-white is-unselectable is-hidden-mobile"
             :class="{'is-paddingless': toggleDataOverlayPanel }"
             title="Click to show the data overlay panel" @click="toggleDataOverlayPanel = !toggleDataOverlayPanel">
          <p class="is-size-5 has-text-centered has-text-weight-bold">
            <span class="icon">
              <i class="fa"
                 :class="{ 'fa-arrow-left': !toggleDataOverlayPanel, 'fa-arrow-right': toggleDataOverlayPanel}"></i>
            </span><br>
            D<br>A<br>T<br>A<br><br>
            O<br>V<br>E<br>R<br>L<br>A<br>Y<br>
            <span class="icon">
              <i class="fa"
                 :class="{ 'fa-arrow-left': !toggleDataOverlayPanel, 'fa-arrow-right': toggleDataOverlayPanel}"></i>
            </span>
          </p>
        </div>
        <DataOverlay v-show="isMobilePage() || toggleDataOverlayPanel" class="om-3" :model="model"
                     :map-type="currentDisplayedType"
                     :dim="dim" :map-name="currentDisplayedName">
        </DataOverlay>
      </template>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import SidebarDataPanels from '@/components/explorer/mapViewer/SidebarDataPanels';
import DataOverlay from '@/components/explorer/mapViewer/DataOverlay.vue';
import Svgmap from '@/components/explorer/mapViewer/Svgmap';
import D3dforce from '@/components/explorer/mapViewer/D3dforce';
import { default as EventBus } from '@/event-bus';
import { default as messages } from '@/helpers/messages';
import { isMobilePage } from '@/helpers/utils';

export default {
  name: 'MapViewer',
  components: {
    SidebarDataPanels,
    DataOverlay,
    Svgmap,
    D3dforce,
  },
  props: {
    model: Object,
  },
  data() {
    return {
      errorMessage: '',
      loadErrorMesssage: '',
      loadErrorTypeMesssage: 'danger', // or info
      showOverviewScreen: true,
      show2D: true,
      show3D: false,
      requestedType: '',
      requestedName: '',
      currentDisplayedType: '',
      currentDisplayedName: '',
      currentDisplayedData: '',
      has2DCompartmentMaps: false,
      has2DSubsystemMaps: false,
      showLoader: false,
      watchURL: true,
      URLID: null,

      mapsData2D: {
        compartments: {},
        subsystems: {},
      },
      mapsData3D: {
        compartments: {},
        subsystems: {},
      },
      compartmentMapping: {
        dim2D: {},
        dim3D: {},
      },

      selectionData: {
        type: '',
        data: null,
        error: false,
      },
      mapListIsVisible: true,
      showSelectionLoader: false,
      isHoverMenuItem: false,
      toggleDataOverlayPanel: false,
      messages,
    };
  },
  computed: {
    activeSwitch() {
      return !this.showLoader && !this.disabled2D;
    },
    disabled2D() {
      if (this.show2D || !this.currentDisplayedName || this.showLoader) {
        return false;
      }
      if (!this.has2DCompartmentMaps && !this.has2DSubsystemMaps) {
        return true;
      }
      if (this.currentDisplayedType === 'compartment') {
        const altID = this.mapsData3D.compartments[this.currentDisplayedName].alternateDim;
        return !(altID in this.mapsData2D.compartments);
      }
      const altID = this.mapsData3D.subsystems[this.currentDisplayedName].alternateDim;
      return !(altID in this.mapsData2D.subsystems && this.mapsData2D.subsystems[altID].sha);
    },
    dim() {
      return this.show2D ? '2d' : '3d';
    },
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.watchURL) {
        this.checkRoute();
      } else {
        this.watchURL = true;
      }
    },
  },
  created() {
    EventBus.$off('showAction');
    EventBus.$off('updatePanelSelectionData');
    EventBus.$off('unSelectedElement');
    EventBus.$off('startSelectedElement');
    EventBus.$off('endSelectedElement');
    EventBus.$off('loadRNAComplete');

    EventBus.$on('showAction', (type, name, ids, forceReload) => {
      if (this.showLoader) {
        return;
      }
      if (!this.checkValidRequest(type, name)) {
        this.handleLoadComplete(false, messages.mapNotFound, 'danger');
        return;
      }
      this.showOverviewScreen = false; // to get the loader visible
      this.selectionData.data = null;
      if (this.show3D) {
        EventBus.$emit('show3Dnetwork', this.requestedType, this.requestedName, ids);
      } else {
        EventBus.$emit('showSVGmap', this.requestedType, this.requestedName, ids, forceReload);
      }
    });

    EventBus.$on('updatePanelSelectionData', (data) => {
      this.selectionData = data;
    });
    EventBus.$on('unSelectedElement', () => {
      this.selectionData.error = false;
      this.selectionData.data = null;
    });
    EventBus.$on('startSelectedElement', () => {
      this.showSelectionLoader = true;
    });
    EventBus.$on('endSelectedElement', (isSuccess) => {
      this.showSelectionLoader = false;
      this.selectionData.error = !isSuccess;
    });
    EventBus.$on('loadRNAComplete', (isSuccess, errorMessage) => {
      if (!isSuccess) {
        // show error
        this.loadErrorMesssage = errorMessage;
        if (!this.loadErrorMesssage) {
          this.loadErrorMesssage = messages.unknownError;
        }
        this.showLoader = false;
        EventBus.$emit('unselectFirstTissue');
        EventBus.$emit('unselectSecondTissue');
        setTimeout(() => {
          this.loadErrorMesssage = '';
        }, 3000);
        return;
      }
      this.showLoader = false;
    });
  },
  beforeMount() {
    this.getSubComptData(this.model);
  },
  methods: {
    switchDimension() {
      if (!this.activeSwitch) {
        return;
      }
      this.show3D = !this.show3D;
      this.show2D = !this.show2D;
      this.selectedElement = null;
      this.selectionData.data = null;
      if (!this.currentDisplayedType || !this.currentDisplayedName) {
        return;
      }

      if (!this.checkValidRequest(this.currentDisplayedType, this.currentDisplayedName)) {
        this.showMessage(messages.mapNotFound, 'info');
        this.show3D = !this.show3D;
        this.show2D = !this.show2D;
        return;
      }

      if (this.show3D) {
        this.URLID = null;
        EventBus.$emit('show3Dnetwork', this.requestedType, this.requestedName);
      } else {
        EventBus.$emit('destroy3Dnetwork');
        EventBus.$emit('showSVGmap', this.requestedType, this.requestedName, [], true);
      }
    },
    handleLoadComplete(isSuccess, errorMessage, messageType) {
      if (!isSuccess) {
        this.selectionData.data = null;
        this.showMessage(errorMessage, messageType);
        this.currentDisplayedType = '';
        this.currentDisplayedName = '';
        return;
      }
      this.showOverviewScreen = false;
      this.currentDisplayedType = this.requestedType;
      this.currentDisplayedName = this.requestedName;
      if (this.show2D) {
        EventBus.$emit('update3DLoadedComponent', null, null); // reset 3d viewer param
      }
      this.updateURL(this.currentDisplayedType, this.currentDisplayedName, this.URLID);
      this.showLoader = false;

      this.$nextTick(() => {
        EventBus.$emit('reloadGeneExpressionData');
      });
    },
    showMessage(errorMessage, messageType) {
      this.loadErrorMesssage = errorMessage;
      this.loadErrorTypeMesssage = messageType;
      if (!this.loadErrorMesssage) {
        this.loadErrorMesssage = messages.unknownError;
      }
      this.showLoader = false;
      setTimeout(() => {
        this.loadErrorMesssage = '';
      }, 3000);
    },
    getSubComptData(model) {
      axios.get(`${model.database_name}/viewer/`)
        .then((response) => {
          this.mapsData3D.compartments = {};
          response.data.compartment.forEach((c) => {
            this.mapsData3D.compartments[c.id] = c;
            this.mapsData3D.compartments[c.id].alternateDim = c.compartment_svg;
            this.compartmentMapping.dim3D[c.id] = c.compartment_svg;
          });

          this.mapsData2D.compartments = {};
          response.data.compartmentsvg.forEach((c) => {
            this.mapsData2D.compartments[c.id] = c;
            // this.mapsData2D.compartments[c.id].id = c.compartment;
            this.mapsData2D.compartments[c.id].alternateDim = c.compartment;
            this.compartmentMapping.dim2D[c.id] = c.compartment;
          });

          this.has2DCompartmentMaps = Object.keys(this.mapsData2D.compartments).length !== 0;

          this.mapsData3D.subsystems = {};
          response.data.subsystem.forEach((s) => {
            this.mapsData3D.subsystems[s.id] = s;
            this.mapsData3D.subsystems[s.id].alternateDim = s.subsystem_svg;
          });

          this.mapsData2D.subsystems = {};
          response.data.subsystemsvg.forEach((s) => {
            this.mapsData2D.subsystems[s.id] = s;
            // this.mapsData2D.subsystems[s.id].id = s.subsystem;
            this.mapsData2D.subsystems[s.id].alternateDim = s.subsystem;
          });

          this.has2DSubsystemMaps = Object.keys(this.mapsData2D.subsystems).length !== 0;

          if (!this.has2DCompartmentMaps && !this.has2DSubsystemMaps) {
            this.show3D = true;
            this.show2D = false;
          }
          this.checkRoute();
        })
        .catch((error) => {
          switch (error.response.status) {
            default:
              this.errorMessage = messages.unknownError;
          }
        });
    },
    checkRoute() {
      // load maps from url if contains map_id, the url is then cleaned of the id
      if (['viewerCompartment', 'viewerCompartmentRea', 'viewerSubsystem', 'viewerSubsystemRea'].includes(this.$route.name)) {
        const type = this.$route.name.includes('Compartment') ? 'compartment' : 'subsystem';
        const mapID = this.$route.params.id;
        this.URLID = this.$route.params.rid;
        const { dim } = this.$route.query;
        if (!dim) {
          this.show2D = false;
        } else {
          this.show2D = dim.toLowerCase() === '2d' && !this.disabled2D;
        }
        this.show3D = !this.show2D;
        this.$nextTick(() => {
          if (this.URLID) {
            // avoid to run this function twice when remove the reaction ID from the URL
            this.watchURL = false;
          }
          EventBus.$emit('showAction', type, mapID, this.URLID ? [this.URLID] : [], false);
        });
      }
    },
    updateURL(type, mapID) {
      // remove reaction id in url for now
      // this.$router.push(`/explore/map-viewer/${this.model.database_name}/${type}/${mapID}/${URLID}?dim=${this.dim}`);
      this.$router.push(`/explore/map-viewer/${this.model.database_name}/${type}/${mapID}?dim=${this.dim}`);
    },
    checkValidRequest(displayType, displayName) {
      this.requestedType = displayType;
      this.requestedName = displayName;
      if (this.show2D) {
        if (displayType === 'compartment') {
          if (displayName in this.compartmentMapping.dim3D) {
            this.requestedName = this.compartmentMapping.dim3D[displayName];
          }
          return this.requestedName in this.mapsData2D.compartments;
        }
        return this.requestedName in this.mapsData2D.subsystems
         && this.mapsData2D.subsystems[this.requestedName].sha;
      }
      if (displayType === 'compartment') {
        if (displayName in this.compartmentMapping.dim2D) {
          this.requestedName = this.compartmentMapping.dim2D[displayName];
        }
        return this.requestedName in this.mapsData3D.compartments;
      }
      return this.requestedName in this.mapsData3D.subsystems;
    },
    showMap(compartmentOrSubsystemID, type = 'compartment') {
      this.selectionData.data = null;
      this.currentDisplayedName = null;
      this.currentDisplayedType = null;
      if (compartmentOrSubsystemID) {
        EventBus.$emit('showAction', type, compartmentOrSubsystemID, [], false);
      } else {
        this.loadedTissue1 = '';
        this.requestedTissue1 = '';
        this.loadedTissue2 = '';
        this.requestedTissue2 = '';
        this.showOverviewScreen = true;
        this.$router.push(`/explore/map-viewer/${this.model.database_name}/`);
        // keep the loaded 2D map, and data info in the 'back', to quickly reload it
      }
    },
    isMobilePage,
  },
};
</script>

<style lang="scss">
#mapViewer {
  #graphframe {
    overflow: hidden;
  }

  #iMainPanel {
    margin-bottom: 0;
  }

  #iSideBar {
    padding: 0.75rem 0 0 0.75rem;
    overflow-y: visible;

    &.scroll {
      overflow-y: scroll;
    }

    #menuButtons {
      display: flex;
      justify-content: space-around;
      padding: 0.75rem;
      button {
        width: 42%;
      }
    }
  }

  #iLoader {
    background: black;
    width: 100%;
    opacity: 0.8;
    display: table;
    a {
      color: white;
      font-size: 5em;
      display: table-cell;
      vertical-align: middle;
      background: black;
      border: 0;
    }
  }

  .fixed-height {
    @media (min-width: $tablet) {
      min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
      max-height: calc(100vh - #{$navbar-height} - #{$footer-height});
      height: calc(100vh - #{$navbar-height} - #{$footer-height});
    }
    @media (max-width: $tablet) {
      min-height: 450px;
      max-height: 450px;
      height: 450px;
    }
    &.mapframe {
      padding: 0;
      margin: 0;
      overflow-y: hidden;
    }

  }

  #dataOverlayBar {
    display: flex;
    align-items: center;
    background: $primary;
    cursor: pointer;
    line-height: 17px;
    padding: 0.25rem;
    .icon {
      padding-bottom: 20px;
      padding-top: 20px;
    }
    &:hover{
      background: $primary-light;
    }
    padding-right: 1rem;
  }

  .overlay {
    position: absolute;
    padding: 10px;
    border-radius: 5px;
    background: rgba(22, 22, 22, 0.8);
  }

  .canvasOption {
    top: 2.25rem;
    left: 2.25rem;
    span {
      display: block;
      &:not(:last-child) {
        margin-bottom: 5px;
      }
    }
  }

  #errorBar {
    z-index: 11;
    position: absolute;
    margin: 0;
    right: 0;
    bottom: 35px;
    border: 1px solid gray;
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

  @media (max-width: $tablet) {
    .ordered-mobile {
      display: flex;
      flex-flow: column;
    }
    .om-1 {
      order: 1;
    }
    .om-2 {
      order: 2;
    }
    .om-3 {
      order: 3;
    }
    .om-4 {
      order: 4;
    }
  }

}

</style>
