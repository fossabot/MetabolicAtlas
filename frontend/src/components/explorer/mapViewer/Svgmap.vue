<template>
  <div class="svgbox">
    <div id="svg-wrapper" v-html="svgContent">
    </div>
    <div class="canvasOption overlay">
      <span class="button" title="Zoom in" @click="zoomOut(false)"><i class="fa fa-search-plus"></i></span>
      <span class="button" title="Zoom out" @click="zoomOut(true)"><i class="fa fa-search-minus"></i></span>
      <span class="button" title="Show/Hide genes"
            style="padding: 4.25px;"
            @click="toggleGenes()">
        <i class="fa fa-eye-slash">&thinsp;G</i>
      </span>
      <span class="button" style="padding: 4.25px;"
            title="Show/Hide subsystem"
            @click="toggleSubsystems()">
        <i class="fa fa-eye-slash">&thinsp;S</i>
      </span>
      <span class="button" title="Toggle fullscreen"
            :disabled="isFullScreenDisabled"
            @click="toggleFullScreen()">
        <i class="fa" :class="{ 'fa-compress': isFullscreen, 'fa-arrows-alt': !isFullscreen}"></i>
      </span>
      <span class="button" title="Download as SVG" @click="downloadMap()"><i class="fa fa-download"></i></span>
    </div>
    <MapSearch ref="mapsearch" :model="model" :matches="searchedNodesOnMap" :ready="loadedMap !== null"
               :fullscreen="isFullscreen" @searchOnMap="searchIDsOnMap" @centerViewOn="centerElementOnSVG"
               @unHighlightAll="unHighlight"></MapSearch>
    <div id="tooltip" ref="tooltip"></div>
  </div>
</template>

<script>

import axios from 'axios';
import $ from 'jquery';
import JQPanZoom from 'jquery.panzoom';
import JQMouseWheel from 'jquery-mousewheel';
import { default as FileSaver } from 'file-saver';
import { debounce } from 'vue-debounce';
import MapSearch from '@/components/explorer/mapViewer/MapSearch';
import { default as EventBus } from '@/event-bus';
import { default as messages } from '@/helpers/messages';
// import { default as queue } from '@/helpers/Queue.src.js';
import { reformatChemicalReactionHTML } from '@/helpers/utils';

// hack: the only way for jquery plugins to play nice with the plugins inside Vue
$.Panzoom = JQPanZoom;
$.fn.extend({
  mousewheel: function fn(options) {
    return this.each(function f() { return JQMouseWheel.mousewheel(this, options); });
  },
  unmousewheel: function fn() {
    return this.each(function f() { return JQMouseWheel.unmousewheel(this); });
  },
});


export default {
  name: 'Svgmap',
  components: {
    MapSearch,
  },
  props: {
    model: Object,
    mapsData: Object,
  },
  data() {
    return {
      errorMessage: '',
      loadedMap: null,
      loadedMapType: null,
      loadedMapHistory: {},
      svgContent: null,
      svgContentHistory: {},
      svgName: '',
      isFullscreen: false,

      $panzoom: null,
      panzoomOptions: {
        maxScale: 1,
        minScale: 0.03,
        increment: 0.025,
        animate: false,
        linearZoom: true,
      },
      currentZoomScale: 1,

      selectIDs: [],
      selectedNodesOnMap: [],
      selectedElemsHL: [],

      searchedNodesOnMap: [],
      searchedElemsHL: [],

      coords: null,

      selectedItemHistory: {},
      selectedElementID: null,
      searchTerm: '',

      HPARNAlevels: {}, // enz id as key, [current tissue level, color] as value
      svgMapURL: process.env.VUE_APP_SVGMAPURL,
      defaultGeneColor: '#feb',
      messages,
    };
  },
  computed: {
    isFullScreenDisabled() {
      if ((document.fullScreenElement !== undefined && document.fullScreenElement === null)
        || (document.msFullscreenElement !== undefined && document.msFullscreenElement === null)
        || (document.mozFullScreen !== undefined && !document.mozFullScreen)
        || (document.webkitIsFullScreen !== undefined && !document.webkitIsFullScreen)) {
        return false;
      }
      return true;
    },
  },
  created() {
    EventBus.$off('showSVGmap');
    EventBus.$off('apply2DHPARNAlevels');
    EventBus.$off('destroy2Dnetwork');

    EventBus.$on('showSVGmap', (type, name, searchTerm, selectIDs, coords, forceReload) => {
      // console.log('showSVGmap', type, name, searchTerm, selectIDs, coords, forceReload);
      if (forceReload) {
        this.svgName = '';
      }
      // set the type, even if might fail to load the map?
      this.loadedMapType = type;
      if (name && (type === 'compartment' || type === 'subsystem')) {
        this.searchTerm = searchTerm;
        this.selectIDs = selectIDs || [];
        this.coords = coords;
        this.loadSVG(name);
      }
    });

    EventBus.$on('apply2DHPARNAlevels', (levels) => {
      this.applyHPARNAlevelsOnMap(levels);
    });

    this.updateURLCoord = debounce(this.updateURLCoord, 150);
  },
  mounted() {
    const self = this;
    ['.met', '.enz', '.rea', '.subsystem'].forEach((aClass) => {
      $('#svg-wrapper').on('click', aClass, function f() {
        self.selectElement($(this));
      });
    });
    $('#svg-wrapper').on('mouseover', '.enz', function f(e) {
      const id = $(this).attr('class').split(' ')[1].trim();
      if (id in self.HPARNAlevels) {
        if (self.HPARNAlevels[id].length === 2) {
          self.$refs.tooltip.innerHTML = `RNA log<sub>2</sub>(TPM+1): ${self.HPARNAlevels[id][1]}`;
        } else {
          self.$refs.tooltip.innerHTML = `RNA log<sub>2</sub>(TPM<sub>T1</sub>+1): ${self.HPARNAlevels[id][2]}<br>`;
          self.$refs.tooltip.innerHTML += `RNA log<sub>2</sub>(TPM<sub>T2</sub>+1): ${self.HPARNAlevels[id][3]}<br>`;
          self.$refs.tooltip.innerHTML += `RNA log<sub>2</sub>(TPM ratio): ${self.HPARNAlevels[id][1]}<br>`;
        }
      } else if (Object.keys(self.HPARNAlevels).length !== 0) {
        self.$refs.tooltip.innerHTML = `RNA log<sub>2</sub>(TPM+1): ${self.HPARNAlevels['n/a'][1]}`;
      } else {
        return;
      }
      self.$refs.tooltip.style.top = `${(e.pageY - $('.svgbox').first().offset().top) + 15}px`;
      self.$refs.tooltip.style.left = `${(e.pageX - $('.svgbox').first().offset().left) + 15}px`;
      self.$refs.tooltip.style.display = 'block';
    });
    $('#svg-wrapper').on('mouseout', '.enz', () => {
      self.$refs.tooltip.innerHTML = '';
      self.$refs.tooltip.style.display = 'none';
    });
    $('.svgbox').on('webkitfullscreenchange mozfullscreenchange fullscreenchange mozFullScreen MSFullscreenChange', (e) => {
      $('.svgbox').first().toggleClass('fullscreen');
      self.isFullscreen = $('.svgbox').first().hasClass('fullscreen');
      e.stopPropagation();
    });
    $(document).on('mozfullscreenchange', () => {
      $('.svgbox').first().toggleClass('fullscreen');
      self.isFullscreen = $('.svgbox').first().hasClass('fullscreen');
    });
  },
  methods: {
    toggleGenes() {
      if ($('.enz, .ee').first().attr('visibility') === 'hidden') {
        $('.enz, .ee').attr('visibility', 'visible');
      } else {
        $('.enz, .ee').attr('visibility', 'hidden');
      }
    },
    toggleSubsystems() {
      if ($('.subsystem').first().attr('visibility') === 'hidden') {
        $('.subsystem').attr('visibility', 'visible');
      } else {
        $('.subsystem').attr('visibility', 'hidden');
      }
    },
    toggleFullScreen() {
      if (this.isFullScreenDisabled) {
        return;
      }
      const elem = $('.svgbox').first()[0];
      if ((document.fullScreenElement !== undefined && document.fullScreenElement === null)
        || (document.msFullscreenElement !== undefined && document.msFullscreenElement === null)
        || (document.mozFullScreen !== undefined && !document.mozFullScreen)
        || (document.webkitIsFullScreen !== undefined && !document.webkitIsFullScreen)) {
        if (elem.requestFullScreen) {
          elem.requestFullScreen();
        } else if (elem.mozRequestFullScreen) {
          elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullScreen) {
          elem.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
        } else if (elem.msRequestFullscreen) {
          elem.msRequestFullscreen();
        }
        this.isFullscreen = true;
      } else {
        if (document.cancelFullScreen) {
          document.cancelFullScreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitCancelFullScreen) {
          document.webkitCancelFullScreen();
        } else if (document.msExitFullscreen) {
          document.msExitFullscreen();
        }
        this.isFullscreen = false;
      }
    },
    zoomOut(bool) {
      if (this.$panzoom) {
        this.$panzoom.panzoom('zoom', bool, {
          focal: {
            clientX: this.clientFocusX(),
            clientY: this.clientFocusY(),
          },
        });
      }
    },
    zoomToValue(v) {
      this.$panzoom.panzoom('zoom', v, {
        increment: 1 - this.currentZoomScale,
        transition: false,
        focal: {
          clientX: this.clientFocusX(),
          clientY: this.clientFocusY(),
        },
      });
    },
    restoreMapPosition(x, y, zoom) {
      this.zoomToValue(1.0);
      this.panToCoords(x, y);
      this.zoomToValue(zoom);
    },
    updateURLCoord(e, v, o) { // eslint-disable-line no-unused-vars
      const zoom = parseFloat(o[0]);
      const panX = -parseFloat(o[4]);
      const panY = -parseFloat(o[5]);
      // FIXME invalid coord
      if (panX !== 0 || panY !== 0 || zoom !== 1) {
        EventBus.$emit('update_url_coord', panX, panY, zoom, 0, 0, 0);
      } else {
        // weird case, happening when a the map is freshly loaded
        EventBus.$emit('update_url_coord', null);
      }
    },
    processSelSearchParam() {
      // unselect
      this.selectedElementID = null;
      this.unHighlight(this.searchedElemsHL, 'schhl');
      this.unHighlight(this.selectedElemsHL, 'selhl');
      if (this.searchTerm) {
        this.$refs.mapsearch.search(this.searchTerm);
      } else if (this.coords) {
        const coords = this.coords.split(',');
        this.restoreMapPosition(coords[0], coords[1], coords[2]);
        this.coords = null;
      }
      // selection (sidebar), get the first node with this id
      const elms = this.findElementsOnSVG(this.selectIDs);
      this.selectElement(elms[0] || null);
    },
    loadSvgPanZoom() {
      // load the lib svgPanZoom on the SVG loaded
      if (!this.$panzoom) {
        this.$panzoom = $('#svg-wrapper').panzoom(this.panzoomOptions);
      } else {
        this.$panzoom = $('#svg-wrapper').panzoom('reset', this.panzoomOptions);
        this.$panzoom.off('mousewheel.focal');
        this.$panzoom.off('panzoomzoom');
        this.$panzoom.off('panzoomchange');
      }
      setTimeout(() => {
        const minZoomScale = Math.min($('.svgbox').width() / $('#svg-wrapper svg').width(),
          $('.svgbox').height() / $('#svg-wrapper svg').height());
        const focusX = ($('#svg-wrapper svg').width() / 2) - ($('.svgbox').width() / 2);
        const focusY = ($('#svg-wrapper svg').height() / 2) - ($('.svgbox').height() / 2);
        this.$panzoom.panzoom('pan', -focusX, -focusY);
        this.$panzoom.panzoom('zoom', true, {
          increment: 1 - minZoomScale,
          focal: {
            clientX: this.clientFocusX(),
            clientY: this.clientFocusY(),
          },
        });
        this.$panzoom.on('mousewheel.focal', (e) => {
          e.preventDefault();
          const delta = e.delta || e.originalEvent.wheelDelta;
          const zoomOut = delta ? delta < 0 : e.originalEvent.deltaY > 0;
          this.$panzoom.panzoom('zoom', zoomOut, { focal: e });
        });
        this.$panzoom.on('panzoomzoom', (e, panzoom, scale) => { // eslint-disable-line no-unused-vars
          this.currentZoomScale = scale;
        });
        this.$panzoom.on('panzoomchange', (e, v, o) => this.updateURLCoord(e, v, o));

        this.processSelSearchParam();
        this.$emit('loadComplete', true, '');
      }, 0);
    },
    loadSVG(id) {
      // load the svg file from the server
      this.$emit('loading');
      const mapInfo = this.mapsData.compartments[id] || this.mapsData.subsystems[id];
      if (!mapInfo) {
        this.loadedMapType = null;
        this.$emit('loadComplete', false, 'Invalid map ID', 'danger');
        return;
      }

      const newSvgName = mapInfo.filename;
      if (!newSvgName) {
        this.$emit('loadComplete', false, messages.mapNotFound, 'danger');
        return;
      }

      if (newSvgName !== this.svgName) {
        this.$refs.mapsearch.reset();
        if (newSvgName in this.loadedMapHistory) {
          this.svgContent = this.svgContentHistory[newSvgName];
          this.loadedMap = this.loadedMapHistory[newSvgName];
          this.svgName = newSvgName;
          setTimeout(() => {
            this.loadSvgPanZoom();
          }, 0);
        } else {
          axios.get(`${this.svgMapURL}/${this.model.database_name}/${newSvgName}`)
            .then((response) => {
              this.svgContent = response.data;
              this.svgName = newSvgName;
              this.loadedMap = mapInfo;
              this.svgContentHistory[this.svgName] = response.data;
              this.loadedMapHistory[this.svgName] = mapInfo;
              setTimeout(() => {
                this.loadSvgPanZoom();
              }, 0);
            })
            .catch(() => {
              this.$emit('loadComplete', false, messages.mapNotFound, 'danger');
            });
        }
      } else {
        this.loadedMap = mapInfo;
        this.processSelSearchParam();
        this.$emit('loadComplete', true, '');
      }
    },
    downloadMap() {
      const blob = new Blob([document.getElementById('svg-wrapper').innerHTML], {
        type: 'data:text/tsv;charset=utf-8',
      });
      FileSaver.saveAs(blob, `${this.loadedMap.name_id}.svg`);
    },
    applyHPARNAlevelsOnMap(RNAlevels) {
      this.HPARNAlevels = RNAlevels;
      if (Object.keys(this.HPARNAlevels).length === 0) {
        $('#svg-wrapper .enz .shape').attr('fill', this.defaultGeneColor);
        return;
      }

      const allGenes = $('#svg-wrapper .enz');
      Object.values(allGenes).forEach((oneEnz) => {
        try {
          const ID = oneEnz.classList[1];
          if (this.HPARNAlevels[ID] !== undefined) {
            oneEnz.children[0].setAttribute('fill', this.HPARNAlevels[ID][0]); // 0 is the float value, 1 the color hex
          } else {
            oneEnz.children[0].setAttribute('fill', this.HPARNAlevels['n/a'][0]);
          }
        } catch {
          // .values() returns the prop 'length', we don't want that
        }
        return true;
      });

      // update cached selected elements
      Object.keys(this.selectedItemHistory).filter(id => this.HPARNAlevels[id] !== undefined)
        .forEach((ID) => {
          this.selectedItemHistory[ID].rnaLvl = this.HPARNAlevels[ID];
        });
      EventBus.$emit('loadRNAComplete', true, '');
    },
    searchIDsOnMap(ids) {
      this.unHighlight(this.searchedElemsHL, 'schhl');
      this.searchedNodesOnMap = [];
      if (ids) {
        this.searchIDs = ids;
      }
      if (this.searchIDs.length !== 0) {
        this.searchedNodesOnMap = this.findElementsOnSVG(this.searchIDs);
        if (this.searchedNodesOnMap.length !== 0) {
          this.searchedElemsHL = this.highlight(this.searchedNodesOnMap, 'schhl');
          if (this.coords) {
            const coords = this.coords.split(',');
            this.restoreMapPosition(coords[0], coords[1], coords[2]);
            this.coords = null;
          } else {
            this.centerElementOnSVG(this.searchedNodesOnMap[0]);
          }
        }
      }
    },
    findElementsOnSVG(IDs) {
      const elmsOnMap = [];
      for (let i = 0; i < IDs.length; i += 1) {
        const id = IDs[i].trim();
        const rselector = `#svg-wrapper .rea#${id}`;
        let elms = $(rselector);
        if (elms.length < 1) {
          const selectors = `#svg-wrapper .met.${id}, #svg-wrapper .enz.${id}`;
          elms = $(selectors);
        }
        for (let j = 0; j < elms.length; j += 1) {
          elmsOnMap.push($(elms[j]));
        }
      }
      return elmsOnMap;
    },
    centerElementOnSVG(element) {
      if (!element) {
        return;
      }

      // eslint-disable-next-line max-len
      const coords = this.getSvgElemCoordinates(element) || this.getSvgElemCoordinates($(element).find('.shape')[0]);
      if (!coords) {
        return;
      }
      this.panToCoords(coords[4], coords[5]);
    },
    getSvgElemCoordinates(el) {
      // read and parse the transform attribut
      const node = $(el);
      let transform = node.attr('transform');
      if (transform) {
        transform = transform.substring(0, transform.length - 1);
        transform = transform.substring(7, transform.length);
        return transform.split(',').map(parseFloat);
      }
      return null;
    },
    highlight(nodes, className) {
      const elmsSelected = [];
      for (const el of nodes) { // eslint-disable-line no-restricted-syntax
        $(el).addClass(className);
        elmsSelected.push(el);
        if (el.hasClass('rea') && className === 'selhl') {
          const selectors = `#svg-wrapper .met.${el.attr('id')}`;
          const elms = $(selectors);
          for (const con of elms) { // eslint-disable-line no-restricted-syntax
            $(con).addClass(className);
            elmsSelected.push(con);
          }
        }
      }
      return elmsSelected;
    },
    unHighlight(elements, className) { // un-highlight elements
      if (elements.length !== 0) {
        for (let i = 0; i < elements.length; i += 1) {
          $(elements[i]).removeClass(className);
        }
      }
    },
    getElementIdAndType(element) {
      if (element.hasClass('rea')) {
        return [element.attr('id'), 'reaction'];
      } if (element.hasClass('enz')) {
        return [element.attr('class').split(' ')[1], 'gene'];
      } if (element.hasClass('met')) {
        return [element.attr('class').split(' ')[1], 'metabolite'];
      }
      return [element.attr('id'), 'subsystem'];
    },
    selectElement(element) {
      if (!element) {
        return;
      }
      const [id, type] = this.getElementIdAndType(element);
      if (type === 'subsystem' && this.loadedMapType === 'subsystem') {
        // cannot select subsystem on subsystem map
        return;
      }

      if (this.selectedElementID === id) {
        this.unSelectElement();
        return;
      }

      const selectionData = { type, data: null, error: false };
      this.selectedElementID = id;

      this.unHighlight(this.selectedElemsHL, 'selhl');
      if (!element.hasClass('subsystem')) {
        // HL all nodes type but subsystems
        this.selectedElemsHL = this.highlight(this.findElementsOnSVG([id]), 'selhl');
      }

      if (this.selectedItemHistory[id]) {
        selectionData.data = this.selectedItemHistory[id];
        this.$emit('newSelection', selectionData);
        return;
      }

      if (type === 'subsystem') {
        // the sidePanel shows only the id for subsystems
        selectionData.data = { id };
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
          }
          selectionData.data = data;
          this.selectedItemHistory[id] = selectionData.data;
          this.$emit('newSelection', selectionData);
          this.$emit('endSelection', true);
        })
        .catch(() => {
          this.$emit('endSelection', false);
        });
    },
    unSelectElement() {
      this.unHighlight(this.selectedElemsHL, 'selhl');
      this.selectedElementID = null;
      this.selectedElemsHL = [];
      this.$emit('unSelect');
    },
    clientFocusX() {
      return ($('.svgbox').width() / 2) + $('#iSideBar').width();
    },
    clientFocusY() {
      return ($('.svgbox').height() / 2) + $('#navbar').height();
    },
    panToCoords(panX, panY) {
      this.$panzoom.panzoom('zoom', 1.0, {
        increment: 1 - this.currentZoomScale,
        transition: false,
      });
      this.$panzoom.panzoom('pan', -panX + ($('.svgbox').width() / 2), -panY + ($('.svgbox').height() / 2));
      this.$emit('loadComplete', true, '');
    },
    reformatChemicalReactionHTML,
  },
};
</script>

<style lang="scss">
  .met, .rea, .enz {
    .shape, .lbl {
      cursor: pointer;
    }
    &:hover {
      .shape {
        fill: salmon;
      }
      .lbl {
        font-weight: 900;
        text-shadow: 0 0 2px white;
      }
    }
  }

  .svgbox {
    position: relative;
    margin: 0;
    padding: 0;
    width: 100%;
    height:100%;
    &.fullscreen {
      background: white;
    }
  }

  svg .selhl {
    display: inline;
    .shape {
      fill: red;
      display: inline;
    }
  }

  svg .schhl {
    display: inline;
    .shape {
      stroke: orange;
      stroke-width: 5px;
      display: inline;
    }
  }

  #tooltip {
    background: whitesmoke;
    color: black;
    border-radius: 3px;
    border: 1px solid gray;
    padding: 8px;
    position: absolute;
    display: none;
  }

</style>
