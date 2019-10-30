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
    <div id="svgSearch" class="overlay">
      <div class="control" :class="{ 'is-loading' : isLoadingSearch }">
        <input id="searchInput" v-model.trim="searchTerm" data-hj-whitelist
               title="Exact search by id, name, alias. Press Enter for results" class="input"
               type="text" :class="searchInputClass"
               :disabled="!loadedMap" placeholder="Exact search by id, name, alias"
               @keyup.enter="searchComponentIDs()" />
      </div>
      <template v-if="searchTerm && currentSearchMatch">
        <span id="searchResCount" class="button has-text-dark"
              title="Click to center on current match"
              @click="centerElementOnSVG(0)">
          {{ currentSearchMatch }} of {{ totalSearchMatch }}
        </span>
        <span class="button has-text-dark"
              title="Go to previous"
              @click="centerElementOnSVG(-1)"><i class="fa fa-angle-left"></i></span>
        <span class="button has-text-dark"
              title="Go to next"
              @click="centerElementOnSVG(1)"><i class="fa fa-angle-right"></i></span>
        <span class="button has-text-dark"
              title="Highlight all matches"
              @click="highlightElementsFound">Highlight all</span>
      </template>
      <template v-else-if="searchTerm && totalSearchMatch === 0 && haveSearched">
        <span class="has-text-white">{{ messages.searchNoResult }}</span>
      </template>
    </div>
    <div id="tooltip" ref="tooltip"></div>
  </div>
</template>

<script>

import axios from 'axios';
import $ from 'jquery';
import JQPanZoom from 'jquery.panzoom';
import JQMouseWheel from 'jquery-mousewheel';
import { default as FileSaver } from 'file-saver';
import { default as EventBus } from '../../../event-bus';
import { default as messages } from '../../../helpers/messages';
import { reformatChemicalReactionHTML } from '../../../helpers/utils';

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
      mapPos: { x: null, y: null, zoom: null },

      idsFound: [],
      elmsOnMap: [],
      elmsHL: [],

      selectedItemHistory: {},
      selectedElement: null,

      HPARNAlevels: {}, // enz id as key, [current tissue level, color] as value

      searchTerm: '',
      searchInputClass: '',
      isLoadingSearch: false,

      currentSearchMatch: 0,
      totalSearchMatch: 0,
      haveSearched: false,

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
  watch: {
    searchTerm() {
      if (!this.searchTerm) {
        this.unHighlight();
        this.totalSearchMatch = 0;
        this.currentSearchMatch = 0;
        this.searchInputClass = 'is-info';
      }
      this.haveSearched = false;
    },
  },
  created() {
    EventBus.$off('showSVGmap');
    EventBus.$off('apply2DHPARNAlevels');

    EventBus.$on('showSVGmap', (type, name, ids, forceReload) => {
      if (forceReload) {
        this.svgName = '';
      }
      // set the type, even if might fail to load the map?
      this.loadedMapType = type;
      if (name && (type === 'compartment' || type === 'subsystem')) {
        this.idsFound = ids || [];
        if (this.idsFound.length === 1) {
          this.loadSVG(name, this.searchIDsOnMap);
        } else {
          this.loadSVG(name);
        }
      }
    });

    EventBus.$on('apply2DHPARNAlevels', (levels) => {
      this.applyHPARNAlevelsOnMap(levels);
    });
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
      $('#svgSearch').toggleClass('fullscreen');
      e.stopPropagation();
    });
    $(document).on('mozfullscreenchange', () => {
      $('.svgbox').first().toggleClass('fullscreen');
      $('#svgSearch').toggleClass('fullscreen');
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
    loadSvgPanZoom(callback) {
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
        this.$panzoom.on('panzoomchange', (e, v, o) => { // eslint-disable-line no-unused-vars
          console.log('panzoomchange');
          this.mapPos.zoom = parseFloat(o[0]);
          console.log('zoom', this.mapPos.zoom);
          const panX = o[4];
          console.log('panX', panX);
          const panY = o[5];
          console.log('panY', panY);
          this.mapPos.x = -panX + ($('.svgbox').width() / 2);
          console.log('svgX', this.mapPos.x);
          this.mapPos.y = -panY + ($('.svgbox').height() / 2);
          console.log('svgY', this.mapPos.y);
          console.log('ratio', (this.mapPos.x / this.mapPos.y), (this.mapPos.y / this.mapPos.x));
        });
        this.unHighlight();
        if (callback) {
          if (callback === this.findElementsOnSVG) {
            callback(true);
          } else if (callback === this.searchComponentIDs) {
            callback();
          }
        } else {
          this.$emit('loadComplete', true, '');
          // const zoom = 0.525;
          this.restoreMapPosition(496.3, 623.5, 0.6);
        }
      }, 0);
    },
    loadSVG(id, callback) {
      // load the svg file from the server
      this.$emit('loading');

      if (!callback) {
        // reset some values
        this.searchTerm = '';
      }

      let mapInfo = this.mapsData.compartments[id];
      if (!mapInfo) {
        mapInfo = this.mapsData.subsystems[id];
        if (!mapInfo) {
          this.loadedMapType = null;
          this.$emit('loadComplete', false, 'Invalid map ID', 'danger');
          return;
        }
      }
      const newSvgName = mapInfo.filename;
      if (!newSvgName) {
        this.$emit('loadComplete', false, messages.mapNotFound, 'danger');
        return;
      }

      if (newSvgName !== this.svgName) {
        if (newSvgName in this.loadedMapHistory) {
          this.svgContent = this.svgContentHistory[newSvgName];
          this.loadedMap = this.loadedMapHistory[newSvgName];
          this.svgName = newSvgName;
          setTimeout(() => {
            this.loadSvgPanZoom(callback);
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
                this.loadSvgPanZoom(callback);
              }, 0);
            })
            .catch(() => {
              this.$emit('loadComplete', false, messages.mapNotFound, 'danger');
            });
        }
      } else {
        this.loadedMap = mapInfo;
        // if already loaded, just call the callback funtion
        if (callback) {
          callback();
        }
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
          // .values() get the prop length, we don't want that
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
    searchComponentIDs() {
      // get the correct IDs from the backend
      this.totalSearchMatch = 0;
      this.currentSearchMatch = 0;
      this.unHighlight();
      if (!this.searchTerm) {
        this.searchInputClass = 'is-warning';
        return;
      }
      this.isLoadingSearch = true;
      axios.get(`${this.model.database_name}/get_id/${this.searchTerm}`)
        .then((response) => {
          // results are on the model, but may not be on the map!
          this.idsFound = response.data;
          this.findElementsOnSVG(true);
        })
        .catch(() => {
          this.searchInputClass = 'is-danger';
        })
        .then(() => {
          this.isLoadingSearch = false;
          this.haveSearched = true;
        });
    },
    findElementsOnSVG(zoomOn) {
      if (!this.idsFound) {
        return;
      }
      this.elmFound = [];
      this.totalSearchMatch = 0;
      for (let i = 0; i < this.idsFound.length; i += 1) {
        const id = this.idsFound[i].trim();
        const rselector = `#svg-wrapper .rea#${id}`;
        let elms = $(rselector);
        if (elms.length < 1) {
          const selectors = `#svg-wrapper .met.${id}, #svg-wrapper .enz.${id}`;
          elms = $(selectors);
        }
        this.totalSearchMatch += elms.length;
        this.currentSearchMatch = 0;
        for (let j = 0; j < elms.length; j += 1) {
          this.elmFound.push($(elms[j]));
        }
      }
      if (this.elmFound.length === 0) {
        this.searchInputClass = 'is-danger';
        return;
      }
      this.searchInputClass = 'is-success';
      if (zoomOn) {
        this.centerElementOnSVG(1);
      } else {
        this.$emit('loadComplete', true, '');
      }
    },
    centerElementOnSVG(increment) {
      if (this.totalSearchMatch === 0) {
        return;
      }
      this.currentSearchMatch += increment;
      if (this.currentSearchMatch < 1) {
        this.currentSearchMatch = this.totalSearchMatch;
      } else if (this.currentSearchMatch > this.totalSearchMatch) {
        this.currentSearchMatch = 1;
      }
      const currentElem = this.elmFound[this.currentSearchMatch - 1];

      this.unSelectElement();
      this.selectElement(currentElem);

      let coords = this.getSvgElemCoordinates(currentElem);
      if (!coords) {
        coords = this.getSvgElemCoordinates($(currentElem).find('.shape')[0]);
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
    highlightElementsFound() {
      this.highlight(this.elmFound);
    },
    highlight(elements) {
      this.unHighlight();
      for (const el of elements) { // eslint-disable-line no-restricted-syntax
        $(el).addClass('hl');
        this.elmsHL.push(el);
        if (el.hasClass('rea')) {
          const selectors = `#svg-wrapper .met.${el.attr('id')}`;
          const elms = $(selectors);
          for (const con of elms) { // eslint-disable-line no-restricted-syntax
            $(con).addClass('hl');
            this.elmsHL.push(con);
          }
        }
      }
    },
    unHighlight() { // un-highlight elements
      if (this.elmsHL.length !== 0) {
        for (let i = 0; i < this.elmsHL.length; i += 1) {
          $(this.elmsHL[i]).removeClass('hl');
        }
        this.elmsHL = [];
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
      const [id, type] = this.getElementIdAndType(element);
      if (type === 'subsystem' && this.loadedMapType === 'subsystem') {
        return;
      }

      if (this.selectedElement && this.selectedElement[0] === element[0]) {
        this.unSelectElement();
        return;
      }

      const selectionData = { type, data: null, error: false };
      this.selectedElement = element;
      if (!element.hasClass('subsystem')) {
        this.highlight([element]);
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
          } else if (type === 'gene') {
          // add the RNA level if any
            if (id in this.HPARNAlevels) {
              data.rnaLvl = this.HPARNAlevels[id];
            }
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
      this.unHighlight();
      this.selectedElement = null;
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
        fill: red;
        stroke-width: 3px;
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

  #svgSearch {
    top: 2.25rem;
    left: 30%;
    margin: 0;
    padding: 15px;
    div {
      display: inline-block;
      vertical-align: middle;
    }
    span {
      margin-left: 5px;
    }
    #searchInput {
      display: inline-block;
      width: 20vw;
    }
    &.fullscreen {
      left: 30%;
      #searchInput {
        width: 30vw;
      }
    }
  }

  svg .hl {
    display: inline;
    .shape {
      fill: red;
      stroke: orange;
      stroke-width: 3;
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
