<template>
  <div id="dataOverlayPanel"
    class="column" style="padding-right: 20px">
    <RNAexpression
      :model="model"
      :mapType="mapType"
      :mapName="mapName"
      @loadedHPARNAtissue="setHPATissues($event)"
      @loadedCustomTissues="setCustomTissues($event)"
      @errorCustomFile="handleErrorCustomFile($event)">
    </RNAexpression>
    <div class="columns">
      <div id="collapseBar" class="column is-narrow is-marginless is-paddingless"
       @click="hidePanel()"
       title="Click to hide the data overlay panel"
       style="display: table;">
        <div style="display: table-cell; vertical-align: middle;">
          <span class="icon">
            <i class="fa fa-arrow-right"></i>
          </span>
        </div>
      </div>
      <div id="dataOverlayContent" class="column">
        <div class="title is-size-4 has-text-centered">Gene expression data</div>
        <div class="has-text-centered">Load custom gene expression data<span class="icon" title="Load An TSV file, with gene IDs and TPM values. More information can be found in the documentation"><i class="fa fa-info-circle"></i></span></div>
        <div id="fileSelectBut" class="file is-centered">
          <label class="file-label">
            <input class="file-input" type="file" name="resume" @change="getFileName">
            <span class="file-cta">
              <span class="file-icon">
                <i class="fa fa-upload"></i>
              </span>
              <span class="file-label">
                Choose a file…
              </span>
            </span>
          </label>
        </div>
        <div id="fileNameBox" v-if="customFileName">
          <div class="tags has-addons is-centered" v-show="!showFileLoader"
            :title="this.errorCustomFile ? this.errorCustomFileMsg : this.customFileInfo">
            <span class="tag" :class="this.errorCustomFile ? 'is-danger' : 'is-success'">
              <div>{{ customFileName }}</div>
            </span>
            <a class="tag is-delete" @click="unloadUploadedFile()" title="Unload file"></a>
          </div>
          <div class="has-text-centered" v-show="showFileLoader">
            <a class="button is-small is-loading"></a>
          </div>
        </div>
        <div class="box card-content-compact">
          <div class="has-text-centered title is-size-6">Data 1</div>
          <div class="control">
            <p>RNA levels from <i>proteinAtlas.org</i><span class="icon" title="HPA expression level are TPM etc.."><i class="fa fa-info-circle"></i></span></p>
            <div class="select is-fullwidth">
              <select v-model="HPATissue1" @change="setFirstTissue('HPA')">
                <option>None</option>
                <option v-for="tissue in HPATissues" class="clickable is-capitalized">{{ tissue }}</option>
              </select>
            </div>
          </div>
          <p>Or uploaded data</p>
          <div class="control">
            <div class="select is-fullwidth">
              <select
              :disabled="disabledCustomSelectData"
              v-model="customTissue1"
              @change="setFirstTissue('custom')">
                <option v-if="!disabledCustomSelectData">None</option>
                <option v-for="tissue in customTissues" class="clickable is-capitalized">{{ tissue }}</option>
              </select>
            </div>
          </div>
        </div>
        <div class="box card-content-compact">
          <div class="has-text-centered title is-size-6">Data 2 (for comparison)</div>
          <div class="control">
            <p>RNA levels from <i>proteinAtlas.org</i><span class="icon"><i class="fa fa-info-circle"></i></span></p>
            <div class="select is-fullwidth">
              <select v-model="HPATissue2" @change="setSecondTissue('HPA')">
                <option>None</option>
                <option v-for="tissue in HPATissues" class="clickable is-capitalized">{{ tissue }}</option>
              </select>
            </div>
          </div>
          <div>Or uploaded data</div>
          <div class="control">
            <div class="select is-fullwidth">
              <select
              :disabled="disabledCustomSelectData"
              v-model="customTissue2"
              @change="setSecondTissue('custom')">
                <option v-if="!disabledCustomSelectData">None</option>
                <option v-for="tissue in customTissues" class="clickable is-capitalized">{{ tissue }}</option>
              </select>
            </div>
          </div>
        </div>
        <div id="RNAlegend" v-html="RNAExpressionLegend"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import RNAexpression from '@/components/explorer/mapViewer/RNAexpression.vue';
import { default as EventBus } from '../../../event-bus';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'DataOverlay',
  props: ['model', 'mapType', 'mapName', 'dim'],
  components: {
    RNAexpression,
  },
  data() {
    return {
      errorMessage: '',

      showLvlCardContent: true,
      HPATissues: [],
      customTissues: ['No file uploaded'],

      RNAExpressionLegend: '',

      HPATissue1: 'None',
      customTissue1: 'No file uploaded',
      HPATissue2: 'None',
      customTissue2: 'No file uploaded',

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
    disabledRNAlvl() {
      return !this.mapName || this.HPATissue.length === 0;
    },
    disabledCustomSelectData() {
      return this.customTissues.length === 1 && this.customTissues[0] === 'No file uploaded';
    },
    isSelectedHPAtissue1() {
      return this.HPATissues.length !== 0 && this.HPATissue1 !== 'None';
    },
    isSelectedHPAtissue2() {
      return this.HPATissues.length !== 0 && this.HPATissue2 !== 'None';
    },
    isSelectedCustomtissue1() {
      return !this.disabledCustomSelectData && !('No file loaded', 'None').includes(this.customTissue1);
    },
    isSelectedCustomtissue2() {
      return !this.disabledCustomSelectData && !('No file loaded', 'None').includes(this.customTissue2);
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
    EventBus.$off('updateRNAExpressionLegend');
    EventBus.$off('reloadGeneExpressionData');
    EventBus.$off('loadingCustomFile');

    EventBus.$on('updateRNAExpressionLegend', (legend) => {
      this.RNAExpressionLegend = legend;
    });

    EventBus.$on('reloadGeneExpressionData', () => {
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
    hidePanel() {
      this.$emit('hidePanel');
    },
    getFileName(e) {
      console.log(e);
      if (e.target.files.length !== 0) {
        this.customFileName = e.target.files[0].name;
        this.errorCustomFile = false;
        this.errorCustomFileMsg = '';
        this.customFileInfo = '';
        EventBus.$emit('loadCustomGeneExpData', e.target.files[0]);
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
        this.customTissue1 = 'No file uploaded';
      } else {
        this.customTissue1 = 'None';
      }
    },
    clearCustomTissue2Selection() {
      if (this.disabledCustomSelectData) {
        this.customTissue2 = 'No file uploaded';
      } else {
        this.customTissue2 = 'None';
      }
    },
    loadRNAlevelsTissue1(tissue, source) {
      if (!tissue) {
        EventBus.$emit('unselectFirstTissue');
      } else {
        EventBus.$emit('selectFirstTissue', tissue, source, this.dim);
      }
    },
    loadRNAlevelsTissue2(tissue, source) {
      if (!tissue) {
        EventBus.$emit('unselectSecondTissue');
      } else {
        EventBus.$emit('selectSecondTissue', tissue, source, this.dim);
      }
    },
    unloadUploadedFile() {
      this.customFileName = '';
      this.customTissues = ['No file uploaded'];
      this.customTissue1 = 'No file uploaded';
      this.customTissue2 = 'No file uploaded';
      if (this.isSelectedTissue1 || this.isSelectedTissue2) {
        EventBus.$emit('selectTissues', this.selectedTissue1, this.tissue1Source, this.selectedTissue2, this.tissue2Source, this.dim);
      }
    },
    handleErrorCustomFile(errorMsg) {
      this.errorCustomFile = true;
      this.errorCustomFileMsg = errorMsg;
      this.showFileLoader = false;
    }
  },
};
</script>

<style lang="scss">
  #dataOverlayPanel {
    .box {
      margin-bottom: 1rem;
      border-radius: 0;
    }
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

  #dataOverlayContent {
    background: lightgray;
    padding-top: 1rem;
  }

  #RNAlegend {
    margin-top: 1rem;
  }

</style>
