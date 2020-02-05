<template>
  <div id="mapViewer" class="extended-section">
    <div id="iMainPanel" class="columns">
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
        <div id="iSideBar" class="column is-one-fifth-widescreen is-one-quarter-desktop
        is-one-quarter-tablet is-half-mobile has-background-lightgray">
          <div id="menu">
            <ul class="l0">
              <li :title="`Select a ${dim.toUpperCase()} compartment network to show`">
                Compartments<span>&nbsp;&#9656;</span>
                <ul class="vhs l1" title="">
                  <li class="has-background-grey-dark clickable" @click="showMap()"><i>Clear selection</i></li>
                  <div v-if="!has2DCompartmentMaps || show3D">
                    <li v-for="cKey in Object.keys(mapsData3D.compartments).sort()" :key="cKey"
                        class="clickable"
                        :class="{'has-text-warning': cKey === currentDisplayedName }"
                        @click="showMap(mapsData3D.compartments[cKey].name_id)">
                      {{ mapsData3D.compartments[cKey].name }}
                      {{ mapsData3D.compartments[cKey].reaction_count != 0 ?
                        `(${mapsData3D.compartments[cKey].reaction_count})` : '' }}
                    </li>
                  </div>
                  <div v-else>
                    <li v-for="cKey in Object.keys(mapsData2D.compartments).sort()" :key="cKey"
                        class="clickable"
                        :class="{ 'disable' : !mapsData2D.compartments[cKey].sha,
                                  'has-text-warning': cKey === currentDisplayedName }"
                        @click="showMap(mapsData2D.compartments[cKey].name_id)">
                      {{ mapsData2D.compartments[cKey].name }}
                      {{ mapsData2D.compartments[cKey].reaction_count != 0 ?
                        `(${mapsData2D.compartments[cKey].reaction_count})` : '' }}
                    </li>
                  </div>
                </ul>
              </li>
              <li :title="`Select a ${dim.toUpperCase()} subsystem network to show`">
                Subsystems<span>&nbsp;&#9656;</span>
                <ul class="vhs l1" title="">
                  <li class="has-background-grey-dark clickable" @click="showMap()"><i>Clear selection</i></li>
                  <div v-if="!has2DSubsystemMaps || show3D">
                    <li v-for="sKey in Object.keys(mapsData3D.subsystems).sort()" :key="sKey"
                        class="clickable"
                        :class="{'has-text-warning': sKey === currentDisplayedName }"
                        @click="showMap(mapsData3D.subsystems[sKey].name_id, 'subsystem')">
                      {{ mapsData3D.subsystems[sKey].name }}
                      {{ mapsData3D.subsystems[sKey].reaction_count != 0 ?
                        `(${mapsData3D.subsystems[sKey].reaction_count})` : '' }}
                    </li>
                  </div>
                  <div v-else>
                    <template v-for="sKey in Object.keys(mapsData2D.subsystems).sort()">
                      <template v-if="mapsData2D.subsystems[sKey].name_id && mapsData2D.subsystems[sKey].sha">
                        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                        <li class="clickable" :class="{'has-text-warning': sKey === currentDisplayedName }"
                            @click="showMap(mapsData2D.subsystems[sKey].name_id, 'subsystem')">
                          {{ mapsData2D.subsystems[sKey].name }}
                          {{ mapsData2D.subsystems[sKey].reaction_count != 0 ?
                            `(${mapsData2D.subsystems[sKey].reaction_count})` : '' }}
                        </li>
                      </template>
                      <template v-else>
                        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                        <li class="disable">
                          {{ mapsData2D.subsystems[sKey].name }}
                        </li>
                      </template>
                    </template>
                  </div>
                </ul>
              </li>
            </ul>
          </div>
          <sidebar-data-panels
            :model="model"
            :dim="dim"
            :map-type="currentDisplayedType"
            :map-name="currentDisplayedName"
            :maps-data="show2D ? mapsData2D : mapsData3D"
            :selection-data="selectionData"
            :loading="showSelectionLoader">
          </sidebar-data-panels>
        </div>
        <div v-show="showOverviewScreen" class="column">
          <p class="is-size-5 has-text-centered" style="padding: 10%;">
            Choose a compartment or subsystem map from the menu on the left
          </p>
        </div>
        <div v-show="!showOverviewScreen" id="graphframe" class="column is-unselectable">
          <svgmap v-show="show2D" :model="model" :maps-data="mapsData2D" @loadComplete="handleLoadComplete"
                  @loading="showLoader=true" @startSelection="showSelectionLoader=true" @endSelection="endSelection"
                  @unSelect="unSelect" @newSelection="newSelection">
          </svgmap>
          <d3dforce v-show="show3D" :model="model" @loadComplete="handleLoadComplete"
                    @loading="showLoader=true" @startSelection="showSelectionLoader=true"
                    @endSelection="endSelection" @unSelect="unSelect" @newSelection="newSelection">
          </d3dforce>
          <div v-show="showLoader" id="iLoader" class="loading">
            <a class="button is-loading"></a>
          </div>
          <div id="iSwitch" class="overlay">
            <span class="button" :disabled="!activeSwitch"
                  :title="activeSwitch ? `Reload the current network in ${ show2D ? '3D' : '2D' }` : ''"
                  @click="switchDimension">
              <template v-if="activeSwitch">
                Switch to&nbsp;<b>{{ show2D ? '3D' : '2D' }}</b>
              </template>
              <template v-else>
                <template v-if="!disabled2D">
                  Switch to&nbsp;<b>{{ show2D ? '3D' : '2D' }}</b>
                </template>
                <template v-else>
                  Not available in 2D
                </template>
              </template>
            </span>
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
             class="column is-narrow has-text-white is-unselectable" :class="{
               'is-paddingless': dataOverlayPanelVisible }"
             title="Click to show the data overlay panel" @click="toggleDataOverlayPanel()">
          <p class="is-size-5 has-text-centered has-text-weight-bold">
            <span class="icon">
              <i class="fa"
                 :class="{ 'fa-arrow-left': !dataOverlayPanelVisible, 'fa-arrow-right': dataOverlayPanelVisible}"></i>
            </span><br>
            D<br>A<br>T<br>A<br><br>
            O<br>V<br>E<br>R<br>L<br>A<br>Y<br>
            <span class="icon">
              <i class="fa"
                 :class="{ 'fa-arrow-left': !dataOverlayPanelVisible, 'fa-arrow-right': dataOverlayPanelVisible}"></i>
            </span>
          </p>
        </div>
        <DataOverlay v-show="dataOverlayPanelVisible" :model="model"
                     :map-type="currentDisplayedType"
                     :dim="dim" :map-name="currentDisplayedName">
        </DataOverlay>
        <URLhandler :model="model" :map-type="currentDisplayedType" :map-name="currentDisplayedName"
          :dim="dim" :sel="selectionData.data" :panel="dataOverlayPanelVisible"></URLhandler>
      </template>
    </div>
  </div>
</template>

<script>
import $ from 'jquery';
import axios from 'axios';
import SidebarDataPanels from '@/components/explorer/mapViewer/SidebarDataPanels';
import URLhandler from '@/components/explorer/mapViewer/URLhandler';
import DataOverlay from '@/components/explorer/mapViewer/DataOverlay.vue';
import Svgmap from '@/components/explorer/mapViewer/Svgmap';
import D3dforce from '@/components/explorer/mapViewer/D3dforce';
import { default as EventBus } from '../../event-bus';
import { default as messages } from '../../helpers/messages';

export default {
  name: 'MapViewer',
  components: {
    SidebarDataPanels,
    DataOverlay,
    Svgmap,
    D3dforce,
    URLhandler,
  },
  props: {
    model: Object,
  },
  data() {
    return {
      errorMessage: '',
      loadErrorMesssage: '',
      loadErrorTypeMesssage: 'danger', // or 'info'
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
      dataOverlayPanelVisible: false,
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
  created() {
    EventBus.$off('showAction');
    EventBus.$off('changeDimension');
    EventBus.$off('togglePanel');
    EventBus.$off('loadRNAComplete');

    EventBus.$on('showAction', (type, name, searchTerm, selectIDS, coords, forceReload) => {
      // console.log('on showAction', type, name, searchTerm, selectIDS, coords, forceReload);
      if (this.showLoader) {
        return;
      }
      if (!this.checkValidRequest(type, name)) {
        this.handleLoadComplete(false, messages.mapNotFound, 'danger');
        return;
      }
      this.showOverviewScreen = false; // to get the loader visible
      this.selectionData.data = null;
      EventBus.$emit(this.show2D ? 'showSVGmap' : 'show3Dnetwork', this.requestedType, this.requestedName, searchTerm, selectIDS, coords, forceReload);
    });

    EventBus.$on('changeDimension', () => {
      this.show2D = !this.show2D;
      this.show3D = !this.show2D;
    });

    EventBus.$on('togglePanel', () => {
      this.toggleDataOverlayPanel();
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

    $('#graphframe').on('click', () => {
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
    toggleDataOverlayPanel() {
      this.dataOverlayPanelVisible = !this.dataOverlayPanelVisible;
      if (this.show3D) {
        // fix the 3D canvas size when open/close dataOverlay
        EventBus.$emit('recompute3DCanvasBounds');
      }
    },
    switchDimension() {
      if (!this.activeSwitch || !this.currentDisplayedType || !this.currentDisplayedName) {
        return;
      }

      if (!this.checkValidRequest(this.currentDisplayedType, this.currentDisplayedName)) {
        this.showMessage(messages.mapNotFound, 'info');
        return;
      }

      this.show3D = !this.show3D;
      this.show2D = !this.show2D;

      // FIXME '_' duplicate with URLhandle
      const searchTerm = this.$route.query.search === '_' ? null : this.$route.query.search;
      const selectIDs = this.$route.query.sel === '_' ? null : [this.$route.query.sel];
      // coord is not maintained and set to null

      if (this.show3D) {
        EventBus.$emit('show3Dnetwork', this.requestedType, this.requestedName, searchTerm, selectIDs, null, true);
      } else {
        EventBus.$emit('showSVGmap', this.requestedType, this.requestedName, searchTerm, selectIDs, null, true);
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
            this.mapsData3D.compartments[c.name_id] = c;
            this.mapsData3D.compartments[c.name_id].id = c.name_id;
            this.mapsData3D.compartments[c.name_id].alternateDim = c.compartment_svg;
            this.compartmentMapping.dim2D[c.compartment_svg] = c.name_id;
          });

          this.mapsData2D.compartments = {};
          response.data.compartmentsvg.forEach((c) => {
            this.mapsData2D.compartments[c.name_id] = c;
            this.mapsData2D.compartments[c.name_id].id = c.compartment;
            this.mapsData2D.compartments[c.name_id].alternateDim = c.compartment;
            this.compartmentMapping.dim3D[c.compartment] = c.name_id;
          });

          this.has2DCompartmentMaps = Object.keys(this.mapsData2D.compartments).length !== 0;

          this.mapsData3D.subsystems = {};
          response.data.subsystem.forEach((s) => {
            this.mapsData3D.subsystems[s.name_id] = s;
            this.mapsData3D.subsystems[s.name_id].id = s.name_id;
            this.mapsData3D.subsystems[s.name_id].alternateDim = s.subsystem_svg;
          });

          this.mapsData2D.subsystems = {};
          response.data.subsystemsvg.forEach((s) => {
            this.mapsData2D.subsystems[s.name_id] = s;
            this.mapsData2D.subsystems[s.name_id].id = s.subsystem;
            this.mapsData2D.subsystems[s.name_id].alternateDim = s.subsystem;
          });

          this.has2DSubsystemMaps = Object.keys(this.mapsData2D.subsystems).length !== 0;

          if (!this.has2DCompartmentMaps && !this.has2DSubsystemMaps) {
            this.show3D = true;
            this.show2D = false;
          }
          EventBus.$emit('checkRoute', 'from mapviewer');
        })
        .catch((error) => {
          switch (error.response.status) {
            default:
              this.errorMessage = messages.unknownError;
          }
        });
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
      this.hideDropleftMenus();
      if (compartmentOrSubsystemID) {
        EventBus.$emit('showAction', type, compartmentOrSubsystemID, '', [], null, false);
      } else {
        this.currentDisplayedType = '';
        this.currentDisplayedName = '';
        this.showOverviewScreen = true;
        this.$router.push({ name: 'viewerRoot', params: { model: this.model.database_name } });
      }
    },
    endSelection(isSuccess) {
      this.showSelectionLoader = false;
      this.selectionData.error = !isSuccess;
    },
    unSelect() {
      this.selectionData.error = false;
      this.selectionData.data = null;
    },
    newSelection(data) {
      this.selectionData = data;
    },
  },
};
</script>

<style lang="scss">
#mapViewer {
  #menu {
    background: $primary;
    color: $white;
    position: relative;
    font-size: 16px;
    ul {
      list-style: none;
      &.vhs, &.l2 {
        max-height: 65vh;
        overflow-y: auto;
      }
    }

    ul.l1, ul.l2 {
      display: none;
      border-left: 1px solid white;
      position: absolute;
      top: 0;
      left: 100%;
      width: 100%;
      background: $primary;
      z-index: 11;
      box-shadow: 5px 5px 5px #222222;
    }

    li {
      padding: 17px 15px 17px 20px;
      border-bottom: 1px solid $grey-lighter;
      user-select: none;
      &:hover {
        background: $primary-light;
      }
      span {
        position: absolute;
        right: 10px;
      }
      &.disable {
        cursor: not-allowed;
        background: $primary;
        color: $grey;
      }
    }
  }

  #iMainPanel {
    margin-bottom: 0;
    min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    height: calc(100vh - #{$navbar-height} - #{$footer-height});
  }

  #iSwitch {
    left: 2.25rem;
    top:  2.25rem;
  }

  #iSideBar {
    padding: 0.75rem 0 0 0.75rem;
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
    z-index: 10;
    padding: 10px;
    border-radius: 5px;
    background: rgba(22, 22, 22, 0.8);
  }

  .canvasOption {
    top: 7.25rem;
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
}

</style>
