<template>
  <div id="dataOverlayPanel"
    class="column" style="padding-right: 20px">
    <RNAexpression
      :model="model"
      :mapType="mapType"
      :mapName="mapName"
      @loadedHPARNAtissue="setHPATissues($event)"
      @firstTissueSelected="setFirstTissue($event)"
      @secondTissueSelected="setSecondTissue($event)">
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
        <div class="has-text-centered">
          <br>
          <div class="title is-size-4">Gene expression data</div>
          Load custom gene expression data [i]:
          <br>
          <div class="file has-name">
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
              <span class="file-name">
                {{ customFileName }}
              </span>
            </label>
          </div>
          <br>
          <div class="box has-text-centered">
            <div class="has-text-weight-bold">Data 1</div>
            <div class="control" style="text-align: center; width: auto">
              <div class="has-text-centered" style="margin: 10px 0">RNA levels from <i>proteinAtlas.org</i> [i]</div>
              <div class="select" v-model="HPATissue1">
                <select v-model="HPATissue1" @change="setFirstTissue('HPA')">
                  <option>None</option>
                  <option v-for="tissue in HPATissues" class="clickable is-capitalized">{{ tissue }}</option>
                </select>
              </div>
            </div>
            <div style="margin: 10px 0">OR uploaded data</div>
            <div class="control" style="text-align: center; width: auto">
              <div class="select">
                <select 
                :disabled="CustomTissues.length === 1 && CustomTissues[0] == 'No file loaded'" 
                v-model="customTissue1"
                @change="setFirstTissue('custom')">
                  <option v-for="tissue in CustomTissues" class="clickable is-capitalized">{{ tissue }}</option>
                </select>
              </div>
            </div>
          </div>
          <div class="box has-text-centered">
            <div class="has-text-weight-bold">Data 2 (optional) [i]</div>
            <div class="control" style="text-align: center; width: auto">
              <div class="has-text-centered" style="margin: 10px 0">RNA levels from <i>proteinAtlas.org</i> [i]</div>
              <div class="select">
                <select v-model="HPATissue2" @change="setSecondTissue('HPA')">
                  <option>None</option>
                  <option v-for="tissue in HPATissues" class="clickable is-capitalized">{{ tissue }}</option>
                </select>
              </div>
            </div>
            <div style="margin: 10px 0">OR uploaded data</div>
            <div class="control" style="text-align: center; width: auto">
              <div class="select">
                <select 
                :disabled="CustomTissues.length === 1 && CustomTissues[0] == 'No file loaded'" 
                v-model="customTissue2"
                @change="setSecondTissue('custom')">
                  <option v-for="tissue in CustomTissues" class="clickable is-capitalized">{{ tissue }}</option>
                </select>
              </div>
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
      CustomTissues: ['No file loaded'],

      RNAExpressionLegend: '',

      HPATissue1: 'None',
      customTissue1: 'No file loaded',
      HPATissue2: 'None',
      customTissue2: 'No file loaded',

      customFileName: '...',
    };
  },
  computed: {
    disabledRNAlvl() {
      return !this.mapName || this.HPATissue.length === 0;
    },
  },
  created() {
    EventBus.$off('updateRNAExpressionLegend');

    EventBus.$on('updateRNAExpressionLegend', (legend) => {
      this.RNAExpressionLegend = legend;
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
      }
    },
    setHPATissues(tissues) {
      this.HPATissues = tissues;
    },
    setFirstTissue(source) {
      if (source === 'HPA') {
        this.loadHPARNAlevelsTissue1(this.HPATissue1);
      } else {

      }
    },
    setSecondTissue(source) {
      if (source === 'HPA') {
        this.loadHPARNAlevelsTissue2(this.HPATissue2);
      } else {

      }
    },
    clearTissue1Selection() {
      EventBus.$emit('unselectFirstTissue');
    },
    clearTissue2Selection() {
      EventBus.$emit('unselectSecondTissue');
    },
    loadHPARNAlevelsTissue1(tissue) {
      if (tissue === 'None') {
        EventBus.$emit('unselectFirstTissue');
      } else {
        EventBus.$emit('selectFirstTissue', tissue, this.dim);
      }
    },
    loadHPARNAlevelsTissue2(tissue) {
      if (tissue === 'None') {
        EventBus.$emit('unselectSecondTissue');
      } else {
        EventBus.$emit('selectSecondTissue', tissue, this.dim);
      }
    },
    getRNATitle() {
      if (this.HPATissue.length === 0) {
        return `RNA expression levels not available for ${this.model.short_name}`;
      }
      return this.disabledRNAlvl ? 'RNA expression levels disabled, select a map first' : 'Select a tissue from the list to color genes according their expression levels in that tissue';
    },
  },
};
</script>

<style lang="scss">
  
  #collapsePanBut {
    border-radius: 15px;
  }

  #dataOverlayPanel {
    .box {
      border-radius: 0;
      &:not(:last-child) {
        margin-bottom: 1rem;
      }
    }
    overflow: auto;
  }

  #dataOverlayContent {
    background: lightgray;
    overflow: auto;
  }

  #RNAlegend {
    margin-top: 1rem;
  }

</style>
