<template>
  <div v-if="mode === 'single'">
    <RNALegend></RNALegend>
  </div>
  <div v-else-if="mode === 'comparison'">
    <RNALegend text="log<sub>2</sub>(TPM<sub>T2</sub>+1 / TPM<sub>T1</sub>+1)" left-value="-5"
               right-value="5"
               :gradient="`${multipleColors}`" natext="n/a"></RNALegend>
  </div>
  <div v-else>
  </div>
</template>

<script>
import axios from 'axios';
import { default as EventBus } from '../../../event-bus';
import RNALegend from '@/components/explorer/mapViewer/RNALegend.vue';
import { getSingleRNAExpressionColor, getComparisonRNAExpressionColor, multipleColors } from '@/expression-sources/hpa';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'RNAexpression',
  components: {
    RNALegend,
  },
  props: {
    model: Object,
    mapType: String,
    mapName: String,
  },
  data() {
    return {
      errorMessage: '',
      tissue1: 'None',
      tissue2: 'None',
      tissue1Source: '',
      tissue2Source: '',
      dim: null,

      HPATissues: [],
      customTissues: [],

      HPARNAlevelsHistory: {},
      customRNALevels: {},

      firstRNAlevels: {},
      secondRNAlevels: {},

      computedRNAlevels: {}, // enz id as key, current tissue level as value
      multipleColors,
    };
  },
  computed: {
    mode() {
      if (this.tissue1 !== 'None' && this.tissue2 !== 'None') {
        return 'comparison';
      } if (this.tissue1 !== 'None' || this.tissue2 !== 'None') {
        return 'single';
      }
      return 'inactive';
    },
  },
  created() {
    EventBus.$off('selectTissues');
    EventBus.$off('selectFirstTissue');
    EventBus.$off('selectSecondTissue');
    EventBus.$off('unselectFirstTissue');
    EventBus.$off('unselectSecondTissue');
    EventBus.$off('loadCustomGeneExpData');

    EventBus.$on('selectTissues', (tissue1, tissue1Source, tissue2, tissue2Source, dim) => {
      if (!tissue1) {
        EventBus.$emit('unselectFirstTissue', true);
        if (tissue2) {
          EventBus.$emit('selectSecondTissue', tissue2, tissue2Source, dim);
        } else {
          EventBus.$emit('unselectSecondTissue');
        }
      } else if (!tissue2) {
        EventBus.$emit('unselectSecondTissue', true);
        EventBus.$emit('selectFirstTissue', tissue1, tissue1Source, dim);
      } else {
        // EventBus.$emit('selectFirstTissue', tissue1, tissue1Source, dim, true);
        // EventBus.$emit('selectSecondTissue', tissue2, tissue2Source, dim);
        this.selectFirstTissue(tissue1, tissue1Source, dim, true);
        this.selectSecondTissue(tissue2, tissue2Source, dim);
      }
    });

    EventBus.$on('selectFirstTissue', (tissue, tissueSource, dim, skipCompute = false) => {
      this.selectFirstTissue(tissue, tissueSource, dim, skipCompute);
    });

    EventBus.$on('selectSecondTissue', (tissue, tissueSource, dim, skipCompute = false) => {
      this.selectSecondTissue(tissue, tissueSource, dim, skipCompute);
    });

    EventBus.$on('unselectFirstTissue', (skipCompute) => {
      this.tissue1 = 'None';
      this.tissue1Source = '';
      this.firstRNAlevels = {};
      if (!skipCompute) {
        this.computeRNAlevels();
      }
    });

    EventBus.$on('unselectSecondTissue', (skipCompute) => {
      this.tissue2 = 'None';
      this.tissue2Source = '';
      this.secondRNAlevels = {};
      if (!skipCompute) {
        this.computeRNAlevels();
      }
    });

    EventBus.$on('loadCustomGeneExpData', (file) => {
      this.loadCustomRNAlevels(file);
    });
    this.getHPATissues();
  },
  methods: {
    selectFirstTissue(tissue, tissueSource, dim, skipCompute = false) {
      this.dim = dim;
      this.tissue1 = tissue;
      this.tissue1Source = tissueSource;
      if (tissueSource === 'HPA') {
        this.loadHPAlevels(tissue, dim, 0, skipCompute ? null : this.computeRNAlevels);
      } else {
        this.parseCustomRNAlevels(tissue, 0, skipCompute ? null : this.computeRNAlevels);
      }
      this.$emit('firstTissueSelected', tissue);
    },
    selectSecondTissue(tissue, tissueSource, dim, skipCompute = false) {
      this.dim = dim;
      this.tissue2 = tissue;
      this.tissue2Dource = tissueSource;
      if (tissueSource === 'HPA') {
        this.loadHPAlevels(tissue, dim, 1, skipCompute ? null : this.computeRNAlevels);
      } else {
        this.parseCustomRNAlevels(tissue, 1, skipCompute ? null : this.computeRNAlevels);
      }
      this.$emit('secondTissueSelected', tissue);
    },
    getHPATissues() {
      axios.get(`${this.model.database_name}/gene/hpa_tissue/`)
        .then((response) => {
          this.HPATissues = response.data;
          this.$emit('loadedHPARNAtissue', this.HPATissues);
        })
        .catch((error) => {
          switch (error.response.status) {
            default:
              this.loadErrorMesssage = messages.unknownError;
          }
        });
    },
    loadHPAlevels(tissue, dim, index, callback) {
      // todo : not fetch when tissue is none?
      if (this.mapName in this.HPARNAlevelsHistory && dim in this.HPARNAlevelsHistory[this.mapName]) {
        this.parseHPARNAlevels(tissue, dim, index, callback);
        return;
      }
      axios.get(`${this.model.database_name}/gene/hpa_rna_levels/${this.mapType}/${dim}/${this.mapName}`)
        .then((response) => {
          if (!(this.mapName in this.HPARNAlevelsHistory)) {
            this.HPARNAlevelsHistory[this.mapName] = {};
          }
          this.HPARNAlevelsHistory[this.mapName][dim] = response.data;
          setTimeout(() => {
            this.parseHPARNAlevels(tissue, dim, index, callback);
          }, 0);
        })
        .catch(() => {
          EventBus.$emit('loadRNAComplete', false, '');
        });
    },
    parseHPARNAlevels(tissue, dim, index, callback) {
      const RNAlevels = {};
      const tissueIndex = this.HPARNAlevelsHistory[this.mapName][dim].tissues.indexOf(tissue);
      const { levels } = this.HPARNAlevelsHistory[this.mapName][dim];
      levels.forEach((array) => {
        const enzID = array[0];
        const level = parseFloat(array[1].split(',')[tissueIndex]);
        RNAlevels[enzID] = level;
      });
      RNAlevels['n/a'] = 'n/a';
      if (index === 0) {
        this.firstRNAlevels = RNAlevels;
      } else {
        this.secondRNAlevels = RNAlevels;
      }
      if (callback) {
        callback();
      }
    },
    loadCustomRNAlevels(file) {
      // get the tissues / columns and the series
      this.$emit('loadingCustomFile');
      const reader = new FileReader();

      // assigning handler
      reader.onloadend = (evt) => {
        const lines = evt.target.result.split(/\r?\n/);
        let indexLine = 1;
        // fetch Tissue
        if (lines[0].split('\t').length !== 1) {
          const arrLine = lines[0].split('\t');
          const v = Number(arrLine[1]);
          if (Number.isNaN(v)) {
            this.customTissues = lines[0].split('\t');
            this.customTissues.shift();
            lines.shift();
          } else {
            this.customTissues = [];
            for (let i = 1; i < arrLine.length; i += 1) {
              this.customTissues.push(`serie${i}`);
            }
          }
        } else {
          this.$emit('errorCustomFile', 'Error: invalid TSV format, expect at least two columns');
          return;
        }

        // parse lines
        const data = {};
        // make tissues key;
        for (let i = 0; i < this.customTissues.length; i += 1) {
          const tissue = this.customTissues[i];
          if (tissue in data) {
            this.$emit('errorCustomFile', `Error: duplicated column '${tissue}'`);
            return;
          }
          data[tissue] = {};
        }

        let entriesCount = 0;
        for (let k = 0; k < lines.length; k += 1) {
          const line = lines[k];
          if (line) {
            const arrLine = line.split('\t');
            if (arrLine.length !== this.customTissues.length + 1) {
              this.$emit('errorCustomFile', `Error: invalid number of values line ${indexLine}`);
              return;
            }
            for (let i = 1; i < arrLine.length; i += 1) {
              if (arrLine[i]) {
                const v = Number(arrLine[i]);
                if (Number.isNaN(v)) {
                  this.$emit('errorCustomFile', `Error: invalid value line ${indexLine}`);
                  return;
                }
                data[this.customTissues[i - 1]][arrLine[0]] = v;
              }
            }
            entriesCount += 1;
          }
          indexLine += 1;
        }
        this.customRNALevels = data;
        // return the columns loaded
        const info = { tissues: this.customTissues, entries: entriesCount, series: this.customTissues.length };
        this.$emit('loadedCustomTissues', info);
      };

      // start reading
      reader.readAsText(file);
    },
    parseCustomRNAlevels(tissue, index, callback) {
      const RNAlevels = this.customRNALevels[tissue];
      RNAlevels['n/a'] = 'n/a';
      if (index === 0) {
        this.firstRNAlevels = RNAlevels;
      } else {
        this.secondRNAlevels = RNAlevels;
      }
      if (callback) {
        callback();
      }
    },
    computeRNAlevels() {
      if (Object.keys(this.firstRNAlevels).length === 0 && Object.keys(this.secondRNAlevels).length === 0) {
        // nothing to compute
        EventBus.$emit(this.dim === '2d' ? 'apply2DHPARNAlevels' : 'apply3DHPARNAlevels', {});
        this.RNAExpressionLegend = false;
        return;
      }
      this.computedRNAlevels = {};
      let RNAlevels = null;
      if (this.mode === 'single') {
        RNAlevels = Object.keys(this.firstRNAlevels).length === 0 ? this.secondRNAlevels : this.firstRNAlevels;
        Object.keys(RNAlevels).forEach((enzID) => {
          const level = this.roundValue(Math.log2(RNAlevels[enzID] + 1));
          this.computedRNAlevels[enzID] = [getSingleRNAExpressionColor(level), level];
        });
        this.computedRNAlevels['n/a'] = [getSingleRNAExpressionColor(NaN), 'n/a'];
      } else {
        // comparison
        if (this.tissue1Source === 'HPA' && this.tissue1Source === this.tissue2Source) {
          // HPA tissues data have the same entries, so no need to check for missing geneID
          Object.keys(this.firstRNAlevels).forEach((enzID) => {
            const log2tpm1 = this.roundValue(Math.log2(this.firstRNAlevels[enzID] + 1));
            const log2tpm2 = this.roundValue(Math.log2(this.secondRNAlevels[enzID] + 1));
            const level = this.roundValue(
              Math.log2((this.secondRNAlevels[enzID] + 1) / (this.firstRNAlevels[enzID] + 1))
            );
            this.computedRNAlevels[enzID] = [getComparisonRNAExpressionColor(level), level, log2tpm1, log2tpm2];
          });
        } else {
          // HPA/custom file comparison or custom/custom comparison
          Object.keys(this.firstRNAlevels).forEach((enzID) => {
            const log2tpm1 = this.roundValue(Math.log2(this.firstRNAlevels[enzID] + 1));
            if (enzID in this.secondRNAlevels) {
              const log2tpm2 = this.roundValue(Math.log2(this.secondRNAlevels[enzID] + 1));
              const level = this.roundValue(
                Math.log2((this.secondRNAlevels[enzID] + 1) / (this.firstRNAlevels[enzID] + 1))
              );
              this.computedRNAlevels[enzID] = [getComparisonRNAExpressionColor(level), level, log2tpm1, log2tpm2];
            } else {
              this.computedRNAlevels[enzID] = [getComparisonRNAExpressionColor(NaN), 'n/a', log2tpm1, 'n/a'];
            }
          });
          Object.keys(this.secondRNAlevels)
            .filter(enzID => !(enzID in this.firstRNAlevels))
            .forEach((enzID) => {
              const log2tpm2 = this.roundValue(Math.log2(this.secondRNAlevels[enzID] + 1));
              this.computedRNAlevels[enzID] = [getComparisonRNAExpressionColor(NaN), 'n/a', 'n/a', log2tpm2];
            });
        }
        this.computedRNAlevels['n/a'] = [getComparisonRNAExpressionColor(NaN), 'n/a'];
      }
      this.$nextTick(() => {
        EventBus.$emit(this.dim === '2d' ? 'apply2DHPARNAlevels' : 'apply3DHPARNAlevels', this.computedRNAlevels);
      });
    },
    roundValue(value) {
      return Math.round((value + 0.00001) * 100) / 100;
    },
  },
};
</script>

<style lang="scss"></style>
