<template>
  <div id="mapViewer" class="extended-section">
    <div class="columns" id="iMainPanel" :class="{ 'is-fullheight' : errorMessage}">
      <template v-if="errorMessage">
        <div class="column">
          <br><br>
          <div class="columns">
            <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
              {{ errorMessage }}
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div id="iSideBar" class="column is-one-fifth-widescreen is-one-quarter-desktop is-one-quarter-tablet is-half-mobile is-fullheight">
          <div id="menu">
            <ul class="l0">
              <li :title="`Select a ${dim.toUpperCase()} compartment network to show`">Compartments<span>&nbsp;&#9656;</span>
                <ul class="vhs l1" title="">
                  <li @click="showMap()" class="has-background-grey-dark clickable"><i>Clear selection</i></li>
                  <div v-if="!has2DCompartmentMaps || show3D">
                    <li v-for="cKey in Object.keys(mapsData3D.compartments).sort()" class="clickable"
                      :class="{'has-text-warning': cKey === currentDisplayedName }"
                      @click="showMap(mapsData3D.compartments[cKey].name_id)">
                      {{ mapsData3D.compartments[cKey].name }} {{ mapsData3D.compartments[cKey].reaction_count != 0 ? `(${mapsData3D.compartments[cKey].reaction_count})` : '' }}
                    </li>
                  </div>
                  <div v-else>
                    <li v-for="cKey in Object.keys(mapsData2D.compartments).sort()" class="clickable"
                      :class="{ 'disable' : !mapsData2D.compartments[cKey].sha, 'has-text-warning': cKey === currentDisplayedName }"
                      @click="showMap(mapsData2D.compartments[cKey].name_id)">
                      {{ mapsData2D.compartments[cKey].name }} {{ mapsData2D.compartments[cKey].reaction_count != 0 ? `(${mapsData2D.compartments[cKey].reaction_count})` : '' }}
                    </li>
                  </div>
                </ul>
              </li>
              <li :title="`Select a ${dim.toUpperCase()} subsystem network to show`">Subsystems<span>&nbsp;&#9656;</span>
                <ul class="vhs l1" title="">
                  <li @click="showMap()" class="has-background-grey-dark clickable"><i>Clear selection</i></li>
                  <div v-if="!has2DSubsystemMaps || show3D">
                    <li v-for="sKey in Object.keys(mapsData3D.subsystems).sort()" class="clickable"
                      :class="{'has-text-warning': sKey === currentDisplayedName }"
                      @click="showMap(mapsData3D.subsystems[sKey].name_id, 'subsystem')">
                        {{ mapsData3D.subsystems[sKey].name }} {{ mapsData3D.subsystems[sKey].reaction_count != 0 ? `(${mapsData3D.subsystems[sKey].reaction_count})` : '' }}
                    </li>
                  </div>
                  <div v-else>
                    <li v-for="sKey in Object.keys(mapsData2D.subsystems).sort()" class="clickable"
                      :class="{'has-text-warning': sKey === currentDisplayedName }"
                      v-if="mapsData2D.subsystems[sKey].name_id && mapsData2D.subsystems[sKey].sha" @click="showMap(mapsData2D.subsystems[sKey].name_id, 'subsystem')">
                        {{ mapsData2D.subsystems[sKey].name }} {{ mapsData2D.subsystems[sKey].reaction_count != 0 ? `(${mapsData2D.subsystems[sKey].reaction_count})` : '' }}
                    </li>
                    <li v-else class="disable">
                       {{ mapsData2D.subsystems[sKey].name }}
                    </li>
                  </div>
                </ul>
              </li>
            </ul>
          </div>
          <sidebar-data-panels
            :model="model"
            :dim="dim"
            :mapType="currentDisplayedType"
            :mapName="currentDisplayedName"
            :mapsData="show2D ? mapsData2D : mapsData3D"
            :selectionData="selectionData"
            :loading="showSelectionLoader">
          </sidebar-data-panels>
        </div>
        <div v-show="showOverviewScreen" class="column">
          <p class="is-size-5 has-text-centered" style="padding: 10%;">Choose a compartment or subsystem map from the menu on the left</p>
        </div>
        <div id="graphframe" v-show="!showOverviewScreen" class="column is-unselectable">
          <div id="dataOverlayBar" title="Click to show the data overlay panel" v-show="!showLoader && !toggleDataOverlayPanel">
            <div id="dataOverlayBut" class="column has-background-primary has-text-white" @click="toggleDataOverlayPanel = !toggleDataOverlayPanel">
              <span class="icon">
                <i class="fa fa-arrow-left"></i>
              </span>
              <p class="is-size-5 has-text-centered has-text-weight-bold">
                D&nbsp;&nbsp;<br>A&nbsp;&nbsp;<br>T&nbsp;&nbsp;<br>A&nbsp;&nbsp;<br><br>
                O&nbsp;&nbsp;<br>V&nbsp;&nbsp;<br>E&nbsp;&nbsp;<br>R&nbsp;&nbsp;<br>L&nbsp;&nbsp;<br>A&nbsp;&nbsp;<br>Y&nbsp;&nbsp;
              </p>
              <span class="icon">
                <i class="fa fa-arrow-left"></i>
              </span>
            </div>
          </div>
          <DataOverlay
            :model="model"
            :mapType="currentDisplayedType"
            :mapName="currentDisplayedName"
            :dim="dim"
            @hidePanel="toggleDataOverlayPanel = !toggleDataOverlayPanel"
            v-show="toggleDataOverlayPanel">
          </DataOverlay>
          <div class="is-fullheight">
            <svgmap v-show="show2D" :model="model" :mapsData="mapsData2D"
              @loadComplete="handleLoadComplete"
              @loading="showLoader=true">
            </svgmap>
            <d3dforce v-show="show3D" :model="model"
              @loadComplete="handleLoadComplete"
              @loading="showLoader=true">
            </d3dforce>
          </div>
          <div id="iLoader" class="loading" v-show="showLoader">
            <a class="button is-loading"></a>
          </div>
          <div id="iSwitch" class="overlay">
            <span class="button" @click="switchDimension" :disabled="!activeSwitch"
            :title="activeSwitch ? `Reload the current network in ${dim.toUpperCase()}` : ''">
              <template v-if="activeSwitch">
                Switch to&nbsp;<b>{{ dim.toUpperCase() }}</b>
              </template>
              <template v-else>
                <template v-if="!disabled2D">
                  Switch to&nbsp;<b>{{ dim.toUpperCase() }}</b>
                </template>
                <template v-else>
                  2D disabled
                </template>
              </template>
            </span>
          </div>
          <transition name="slide-fade">
            <article id="errorBar" class="message" v-if="loadErrorMesssage"
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
      </template>
    </div>
  </div>
</template>

<script>
import $ from 'jquery';
import axios from 'axios';
import SidebarDataPanels from '@/components/explorer/mapViewer/SidebarDataPanels';
import DataOverlay from '@/components/explorer/mapViewer/DataOverlay.vue';
import Svgmap from '@/components/explorer/mapViewer/Svgmap';
import D3dforce from '@/components/explorer/mapViewer/D3dforce';
import { default as EventBus } from '../../event-bus';
import { default as messages } from '../../helpers/messages';

export default {
  name: 'map-viewer',
  props: ['model'],
  components: {
    SidebarDataPanels,
    DataOverlay,
    Svgmap,
    D3dforce,
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
      // console.log(`showAction ${type} ${name} ${ids} ${forceReload}`);
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
        console.log('MV show3Dnetwork');
        EventBus.$emit('show3Dnetwork', this.requestedType, this.requestedName, ids);
      } else {
        console.log('MV showSVGmap');
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
    this.setup();
  },
  mounted() {
    // menu
    const self = this;
    $('#menu').on('mouseenter', 'ul.l0 > li:has(ul)', function f() {
      if ($(this).hasClass('disable')) {
        return;
      }
      $('#menu ul.l1, #menu ul.l2').hide();
      $(this).find('ul').first().show();
      self.isHoverMenuItem = true;
    });
    $('#menu').on('mouseleave', 'ul.l0 > li:has(ul)', function f() {
      self.isHoverMenuItem = false;
      $(this).find('ul').first().delay(500)
        .queue(function ff() {
          if (!self.isHoverMenuItem) {
            $(this).hide(0);
          }
          $(this).dequeue();
        });
    });
    $('#menu').on('mouseenter', 'ul.l1 > li:has(ul)', function f() {
      $('#menu ul.l2').hide();
      $(this).find('ul').first().show();
      self.isHoverMenuItem = true;
    });

    $('#graphframe').on('click', function f() {
      $('#menu ul.l1, #menu ul.l2').hide();
    });
  },
  methods: {
    setup() {
      if (!this.model || this.model.database_name !== this.$route.params.model) {
        EventBus.$emit('modelSelected', '');
        this.errorMessage = `Error: ${messages.modelNotFound}`;
        return;
      }
      this.getSubComptData(this.model);
    },
    hideDropleftMenus() {
      $('#menu ul.l1, #menu ul.l2').hide();
    },
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
      this.updateURL(this.requestedType, this.requestedName, this.URLID);
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
        for (const c of response.data.compartment) {
          this.mapsData3D.compartments[c.name_id] = c;
          this.mapsData3D.compartments[c.name_id].id = c.name_id;
          this.mapsData3D.compartments[c.name_id].alternateDim = c.compartment_svg;
          this.compartmentMapping.dim2D[c.compartment_svg] = c.name_id;
        }
        this.mapsData2D.compartments = {};
        for (const c of response.data.compartmentsvg) {
          this.mapsData2D.compartments[c.name_id] = c;
          this.mapsData2D.compartments[c.name_id].id = c.compartment;
          this.mapsData2D.compartments[c.name_id].alternateDim = c.compartment;
          this.compartmentMapping.dim3D[c.compartment] = c.name_id;
        }
        this.has2DCompartmentMaps = Object.keys(this.mapsData2D.compartments).length !== 0;
        this.mapsData3D.subsystems = {};
        for (const s of response.data.subsystem) {
          this.mapsData3D.subsystems[s.name_id] = s;
          this.mapsData3D.subsystems[s.name_id].id = s.name_id;
          this.mapsData3D.subsystems[s.name_id].alternateDim = s.subsystem_svg;
        }
        this.mapsData2D.subsystems = {};
        for (const s of response.data.subsystemsvg) {
          this.mapsData2D.subsystems[s.name_id] = s;
          this.mapsData2D.subsystems[s.name_id].id = s.subsystem;
          this.mapsData2D.subsystems[s.name_id].alternateDim = s.subsystem;
        }
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
        const dim = this.$route.query.dim;
        if (!dim) {
          this.show2D = false;
        } else {
          this.show2D = dim.toLowerCase() === '2d' && !this.disabled2D;
        }
        this.show3D = !this.show2D;
        this.$nextTick(() => {
          EventBus.$emit('showAction', type, mapID, this.URLID ? [this.URLID] : [], false);
        });
        this.updateURL(type, mapID, this.URLID);
      }
    },
    updateURL(type, mapID, URLID) {
      this.watchURL = false;
      if (URLID && false) {
        // no reaction id in url for now
        this.$router.push(`/explore/map-viewer/${this.model.database_name}/${type}/${mapID}/${URLID}?dim=${this.dim}`);
      } else {
        this.$router.push(`/explore/map-viewer/${this.model.database_name}/${type}/${mapID}?dim=${this.dim}`);
      }
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
        return this.requestedName in this.mapsData2D.subsystems &&
         this.mapsData2D.subsystems[this.requestedName].sha;
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
      this.hideDropleftMenus();
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
  },
};
</script>

<style lang="scss">

$navbar-height: 2.5rem;
$footer-height: 4.55rem;

#mapViewer {
  .is-fullheight {
    min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    height: calc(100vh - #{$navbar-height} - #{$footer-height});
  }

  #iMainPanel {
    margin-bottom: 0;
  }

  #iSwitch {
    left: 2.25rem;
    top:  2.25rem;
  }

  #iSideBar {
    padding: 0.75rem 0 0 0.75rem;
    background: lightgray;
  }

  #iLoader {
    z-index: 10;
    position: absolute;
    background: black;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0.8;
    display: table;
    a {
      color: white;
      font-size: 5em;
      font-weight: 1000;
      display: table-cell;
      vertical-align: middle;
      background: black;
      border: 0;
    }
  }

  #graphframe {
    position: relative;
    height: 100%;
    padding: 0;
    margin: 0;
    overflow: hidden;
  }


  #dataOverlayBar {
    position: absolute;
    z-index: 10;
    right: 0;
    min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    height: calc(100vh - #{$navbar-height} - #{$footer-height});
    display: table;
    opacity: 0.7 ;
  }

  #dataOverlayBut {
    display:table-cell;
    vertical-align: middle;
    border: 1px solid black;
    cursor: pointer;
    line-height: 17px;
    padding-left: 10px;
    padding-right: 10px;
    .icon {
      padding-right: 10px;
      padding-bottom: 20px;
      padding-top: 20px;
    }
  }

  #dataOverlayPanel {
    z-index: 13;
    padding: 10px 10px;
    position: absolute;
    right: 0;
    min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(101vh - #{$navbar-height} - #{$footer-height});
    height: calc(101vh - #{$navbar-height} - #{$footer-height});
    border-left: 1px solid gray;
  }

  #collapseBar {
    width: 7%;
    color: white;
    background: $primary;
    min-height: calc(101vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(101vh - #{$navbar-height} - #{$footer-height});
    height: calc(101vh - #{$navbar-height} - #{$footer-height});
    cursor: pointer;
    opacity: 0.7;
  }

  .overlay {
    position: absolute;
    z-index: 10;
    padding: 10px;
    border-radius: 5px;
    background: rgba(22, 22, 22, 0.8);
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
}

</style>
