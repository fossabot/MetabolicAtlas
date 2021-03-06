<template>
  <div class="column is-one-fifth-widescreen is-one-quarter-desktop
              is-one-quarter-tablet is-half-mobile has-background-lightgray"
       style="padding-left: 0; overflow-y: scroll;">
    <div class="title is-size-4 has-text-centered">Gene expression data</div>
    <div class="has-text-centered"
         title="Load a TSV file with gene IDs and TPM values.
         More information can be found in the documentation.">
      Load custom gene expression data<span class="icon"><i class="fa fa-info-circle"></i></span>
    </div>
    <div id="fileSelectBut" class="file is-centered">
      <label class="file-label">
        <input class="file-input"
               type="file"
               name="resume"
               @change="getFileName">
        <span class="file-cta">
          <span class="file-icon">
            <i class="fa fa-upload"></i>
          </span>
          <span class="file-label">
            Choose a file
          </span>
        </span>
      </label>
    </div>
    <div v-if="customFileName" id="fileNameBox">
      <div v-show="!showFileLoader" class="tags has-addons is-centered"
           :title="errorCustomFile ? errorCustomFileMsg : customFileInfo">
        <span class="tag" :class="errorCustomFile ? 'is-danger' : 'is-success'">
          <div class="is-size-6">{{ customFileName }}</div>
        </span>
        <a class="tag is-delete" title="Unload file" @click="unloadUploadedFile()"></a>
      </div>
      <div v-show="showFileLoader" class="has-text-centered">
        <a class="button is-small is-loading"></a>
      </div>
    </div>
    <div class="card card-margin">
      <div class="card-content card-content-compact">
        <div class="has-text-centered title is-size-6">Data 1</div>
        <div class="control">
          <p>RNA levels from <a href="https://www.proteinatlas.org" target="_blank">proteinAtlas.org</a></p>
          <div class="select is-fullwidth">
            <select v-model="HPATissue1" :disabled="disabledRNAlvl" @change="setFirstTissue('HPA')">
              <option>None</option>
              <option v-for="tissue in HPATissues" :key="tissue"
                      class="clickable is-capitalized">{{ tissue }}</option>
            </select>
          </div>
        </div>
        <p>Or uploaded data</p>
        <div class="control">
          <div class="select is-fullwidth">
            <select
              v-model="customTissue1"
              :disabled="disabledCustomSelectData"
              @change="setFirstTissue('custom')">
              <option v-if="!disabledCustomSelectData">None</option>
              <option v-for="tissue in customTissues" :key="tissue"
                      class="clickable is-capitalized">{{ tissue }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    <div class="card card-margin">
      <div class="card-content card-content-compact">
        <div class="has-text-centered title is-size-6">Data 2 (for comparison)</div>
        <div class="control">
          <p>RNA levels from <a href="https://www.proteinatlas.org" target="_blank">proteinAtlas.org</a></p>
          <div class="select is-fullwidth">
            <select v-model="HPATissue2" :disabled="disabledRNAlvl" @change="setSecondTissue('HPA')">
              <option>None</option>
              <option v-for="tissue in HPATissues" :key="tissue"
                      class="clickable is-capitalized">{{ tissue }}</option>
            </select>
          </div>
        </div>
        <div>Or uploaded data</div>
        <div class="control">
          <div class="select is-fullwidth">
            <select
              v-model="customTissue2"
              :disabled="disabledCustomSelectData"
              @change="setSecondTissue('custom')">
              <option v-if="!disabledCustomSelectData">None</option>
              <option v-for="tissue in customTissues"
                      :key="tissue"
                      class="clickable is-capitalized">{{ tissue }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    <RNAexpression class="card-margin"
                   :map-type="mapType"
                   :map-name="mapName"
                   @loadedHPARNAtissue="setHPATissues($event)"
                   @loadedCustomTissues="setCustomTissues($event)"
                   @errorCustomFile="handleErrorCustomFile($event)">
    </RNAexpression>
  </div>
</template>

<script>

import { mapState } from 'vuex';
import $ from 'jquery';
import RNAexpression from '@/components/explorer/mapViewer/RNAexpression.vue';
import { default as EventBus } from '@/event-bus';

const NOFILELOADED = 'No file loaded';

export default {
  name: 'DataOverlay',
  components: {
    RNAexpression,
  },
  props: {
    mapType: String,
    mapName: String,
    dim: String,
  },
  data() {
    return {
      errorMessage: '',

      showLvlCardContent: true,
      HPATissues: [],
      customTissues: [NOFILELOADED],

      HPATissue1: 'None',
      customTissue1: NOFILELOADED,
      HPATissue2: 'None',
      customTissue2: NOFILELOADED,

      tissue1Source: '',
      tissue2Source: '',

      customFileName: '',
      showFileLoader: true,
      errorCustomFile: false,
      errorCustomFileMsg: '',
      customFileInfo: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
    disabledRNAlvl() {
      return !this.mapName || this.HPATissues.length === 0;
    },
    disabledCustomSelectData() {
      return this.customTissues.length === 1 && this.customTissues[0] === NOFILELOADED;
    },
    isSelectedHPAtissue1() {
      return this.HPATissues.length !== 0 && this.HPATissue1 !== 'None';
    },
    isSelectedHPAtissue2() {
      return this.HPATissues.length !== 0 && this.HPATissue2 !== 'None';
    },
    isSelectedCustomtissue1() {
      return !this.disabledCustomSelectData && !(NOFILELOADED, 'None').includes(this.customTissue1);
    },
    isSelectedCustomtissue2() {
      return !this.disabledCustomSelectData && !(NOFILELOADED, 'None').includes(this.customTissue2);
    },
    isSelectedTissue1() {
      return this.isSelectedHPAtissue1 || this.isSelectedCustomtissue1;
    },
    isSelectedTissue2() {
      return this.isSelectedHPAtissue2 || this.isSelectedCustomtissue2;
    },
    selectedTissue1() {
      if (this.isSelectedTissue1) {
        return this.isSelectedHPAtissue1 ? this.HPATissue1 : this.customTissue1;
      }
      return '';
    },
    selectedTissue2() {
      if (this.isSelectedTissue2) {
        return this.isSelectedHPAtissue2 ? this.HPATissue2 : this.customTissue2;
      }
      return '';
    },
  },
  created() {
    EventBus.$off('reloadGeneExpressionData');
    EventBus.$off('loadingCustomFile');

    EventBus.$on('reloadGeneExpressionData', () => {
      // check if tissues are provided in the URL
      if (this.$route.query && (this.$route.query.g1 || this.$route.query.g2)) {
        if (this.$route.query.g1 !== '_' && this.$route.query.g1 !== this.selectedTissue1) {
          if (!this.HPATissues.includes(this.$route.query.g1)) {
            this.HPATissue1 = 'None';
            this.setRouteParam('', null);
          } else {
            this.HPATissue1 = this.$route.query.g1;
            this.tissue1Source = 'HPA';
          }
        }
        if (this.$route.query.g2 !== '_' && this.$route.query.g2 !== this.selectedTissue2) {
          if (!this.HPATissues.includes(this.$route.query.g2)) {
            this.HPATissue2 = 'None';
            this.setRouteParam(null, '');
          } else {
            this.HPATissue2 = this.$route.query.g2;
            this.tissue2Source = 'HPA';
          }
        }
      }
      if (this.isSelectedTissue1 || this.isSelectedTissue2) {
        EventBus.$emit('selectTissues', this.selectedTissue1, this.tissue1Source, this.selectedTissue2, this.tissue2Source, this.dim);
      }
    });

    EventBus.$on('loadedCustomExpressionData', (info) => {
      this.customTissue1 = 'None';
      this.customTissue2 = 'None';
      this.customFileInfo = info;
    });
    EventBus.$on('loadingCustomFile', () => {
      this.showFileLoader = true;
    });
  },
  methods: {
    getFileName(e) {
      if (e.target.files.length !== 0) {
        this.customFileName = e.target.files[0].name;
        this.errorCustomFile = false;
        this.errorCustomFileMsg = '';
        this.customFileInfo = '';
        EventBus.$emit('loadCustomGeneExpData', e.target.files[0]);
        $('.file-input')[0].value = '';
      } else {
        this.customFileName = '';
      }
    },
    setHPATissues(tissues) {
      this.HPATissues = tissues;
    },
    setCustomTissues(info) {
      this.customTissues = info.tissues;
      this.customTissue1 = 'None';
      this.customTissue2 = 'None';
      this.customFileInfo = `Entries found: ${info.entries} - Series loaded: ${info.series}`;
      this.showFileLoader = false;
    },
    setFirstTissue(source) {
      if (source === 'HPA' && this.isSelectedCustomtissue1) {
        this.clearCustomTissue1Selection();
      } else if (source === 'custom' && this.isSelectedHPAtissue1) {
        this.HPATissue1 = 'None';
      }
      this.loadRNAlevelsTissue1(this.selectedTissue1, source);
      this.tissue1Source = source;
    },
    setSecondTissue(source) {
      if (source === 'HPA' && this.isSelectedCustomtissue2) {
        this.clearCustomTissue2Selection();
      } else if (source === 'custom' && this.isSelectedHPAtissue2) {
        this.HPATissue2 = 'None';
      }
      this.loadRNAlevelsTissue2(this.selectedTissue2, source);
      this.tissue2Source = source;
    },
    clearCustomTissue1Selection() {
      if (this.disabledCustomSelectData) {
        this.customTissue1 = NOFILELOADED;
      } else {
        this.customTissue1 = 'None';
      }
    },
    clearCustomTissue2Selection() {
      if (this.disabledCustomSelectData) {
        this.customTissue2 = NOFILELOADED;
      } else {
        this.customTissue2 = 'None';
      }
    },
    loadRNAlevelsTissue1(tissue, source) {
      if (!tissue) {
        EventBus.$emit('unselectFirstTissue');
        this.setRouteParam('', null);
      } else {
        EventBus.$emit('selectFirstTissue', tissue, source, this.dim);
      }
    },
    loadRNAlevelsTissue2(tissue, source) {
      if (!tissue) {
        EventBus.$emit('unselectSecondTissue');
        this.setRouteParam(null, '');
      } else {
        EventBus.$emit('selectSecondTissue', tissue, source, this.dim);
      }
    },
    unloadUploadedFile() {
      this.customFileName = '';
      this.customTissues = [NOFILELOADED];
      this.customTissue1 = NOFILELOADED;
      this.customTissue2 = NOFILELOADED;
      if (this.isSelectedTissue1 || this.isSelectedTissue2) {
        EventBus.$emit('selectTissues', this.selectedTissue1, this.tissue1Source, this.selectedTissue2, this.tissue2Source, this.dim);
      }
    },
    handleErrorCustomFile(errorMsg) {
      this.errorCustomFile = true;
      this.errorCustomFileMsg = errorMsg;
      this.showFileLoader = false;
    },
    setRouteParam(value1, value2) {
      // TODO: refactor to use maps/tissue1 from store instead of HPATissue1
      if (value1 !== null) {
        this.$store.dispatch('maps/setTissue1', value1);
      } else if (value2 !== null) {
        this.$store.dispatch('maps/setTissue2', value2);
      }
    },
  },
};
</script>

<style lang="scss">
#dataOverlayPanel {
  z-index: 13;
  .select {
    margin: 0.5rem 0;
  }
  .title {
    margin-bottom: 0.5rem;
  }
}

#fileSelectBut {
  margin-bottom: 0.5rem;
}

#fileNameBox {
  span.tag {
    width: 90%;
    cursor: help;
      > div {
      white-space: nowrap;
      overflow: hidden;
      max-width: 250px;
      text-overflow: ellipsis;
      cursor: help;
    }
  }
  margin-bottom: 1rem;
}
</style>
