<template></template>

<script>
import axios from 'axios';
import $ from 'jquery';
import { default as EventBus } from '../../../event-bus';
import { getSingleRNAExpressionColor, getComparisonRNAExpressionColor, getSingleExpLvlLegend, getComparisonExpLvlLegend } from '../../../expression-sources/hpa';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'RNAexpression',
  props: ['model', 'mapType', 'mapName'],
  data() {
    return {
      errorMessage: '',
      tissue1: 'None',
      tissue2: 'None',
      dim: null,

      HPATissue: [],
      HPARNAlevelsHistory: {},

      firstRNAlevels: {},
      secondRNAlevels: {},

      computedRNAlevels: {}, // enz id as key, current tissue level as value
    };
  },
  created() {
    EventBus.$off('selectTissues');
    EventBus.$off('selectFirstTissue');
    EventBus.$off('selectSecondTissue');
    EventBus.$off('unselectFirstTissue');
    EventBus.$off('unselectSecondTissue');

    EventBus.$on('selectTissues', (tissue1, tissue2, dim) => {
      if (!tissue1) {
        EventBus.$emit('unselectFirstTissue', true);
        if (tissue2) {
          EventBus.$emit('selectSecondTissue', tissue2, dim);
        } else {
          EventBus.$emit('unselectSecondTissue');
        }
      } else if (!tissue2) {
        EventBus.$emit('unselectSecondTissue', true);
        EventBus.$emit('selectFirstTissue', tissue1, dim);
      } else {
        EventBus.$emit('selectFirstTissue', tissue1, dim, true);
        EventBus.$emit('selectSecondTissue', tissue2, dim);
      }
    });

    EventBus.$on('selectFirstTissue', (tissue, dim, skipCompute = false) => {
      console.log('selectFirstTissue = ', tissue);
      if (!this.isTissueValid(tissue)) {
        // handle error
        console.log('error tissue unknown: ', tissue);
        return;
      }
      // if (this.tissue1 === tissue) {
      //   return;
      // }
      this.selectFirstTissue(tissue, dim, skipCompute);
    });

    EventBus.$on('selectSecondTissue', (tissue, dim, skipCompute = false) => {
      console.log('selectSecondTissue = ', tissue);
      if (!this.isTissueValid(tissue)) {
        // handle error
        console.log('error tissue unknown: ', tissue);
        return;
      }
      // if (this.tissue2 === tissue) {
      //   return;
      // }
      this.selectSecondTissue(tissue, dim, skipCompute);
    });

    EventBus.$on('unselectFirstTissue', (skipCompute) => {
      console.log('unselectFirstTissue');
      // if (this.tissue1 === 'None') {
      //   return;
      // }
      this.tissue1 = 'None';
      this.firstRNAlevels = {};
      if (!skipCompute) {
        this.computeRNAlevels();
      }
      this.$emit('firstTissueSelected', '');
    });

    EventBus.$on('unselectSecondTissue', (skipCompute) => {
      console.log('unselectSecondTissue');
      // if (this.tissue2 === 'None') {
      //   return;
      // }
      this.tissue2 = 'None';
      this.secondRNAlevels = {};
      if (!skipCompute) {
        this.computeRNAlevels();
      }
      this.$emit('secondTissueSelected', '');
    });

    this.getHPATissue();
  },
  computed: {
    mode() {
      let m;
      if (this.tissue1 !== 'None' && this.tissue2 !== 'None') {
        return 'comparison';
      }
      return 'single';
    },
  },
  methods: {
    isTissueValid(tissue) {
      if (!this.HPATissue || this.HPATissue.indexOf(tissue) === -1) {
        return false;
      }
      return true;
    },
    selectFirstTissue(tissue, dim, skipCompute = false) {
      this.dim = dim;
      this.tissue1 = tissue;
      if (!skipCompute) {
        this.loadHPAlevels(tissue, dim, 0, this.computeRNAlevels);
      } else {
        this.loadHPAlevels(tissue, dim, 0, null);
      }
      this.$emit('firstTissueSelected', tissue);
    },
    selectSecondTissue(tissue, dim, skipCompute = false) {
      this.dim = dim;
      this.tissue2 = tissue;
      if (!skipCompute) {
        this.loadHPAlevels(tissue, dim, 1, this.computeRNAlevels);
      } else {
        this.loadHPAlevels(tissue, dim, 1, null);
      }
      this.$emit('secondTissueSelected', tissue);
    },
    getHPATissue() {
      axios.get(`${this.model.database_name}/gene/hpa_tissue/`)
        .then((response) => {
          this.HPATissue = response.data;
          this.$emit('loadedHPARNAtissue', this.HPATissue);
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
      .catch((error) => {
        console.log(error, tissue, dim, index);
        EventBus.$emit('loadRNAComplete', false, '');
        return;
      });
    },
    parseHPARNAlevels(tissue, dim, index, callback) {
      console.log('parseHPARNAlevels ', tissue, dim, index);
      const RNAlevels = {};
      const tissue_index = this.HPARNAlevelsHistory[this.mapName][dim].tissues.indexOf(tissue);
      const levels = this.HPARNAlevelsHistory[this.mapName][dim].levels;
      for (const array of levels) {
        const enzID = array[0];
        let level = parseFloat(array[1].split(',')[tissue_index]);
        RNAlevels[enzID] = level;
      }
      RNAlevels['n/a'] = 'n/a';
      index === 0 ? this.firstRNAlevels = RNAlevels : this.secondRNAlevels = RNAlevels;
      if (callback) {
        callback();
      }
    },
    computeRNAlevels() {
      console.log('computeRNAlevels');
      if (Object.keys(this.firstRNAlevels).length === 0 && Object.keys(this.secondRNAlevels).length === 0) {
        // nothing to compute
        EventBus.$emit(this.dim === '2d' ? 'apply2DHPARNAlevels' : 'apply3DHPARNAlevels' , {});
        EventBus.$emit('updateRNAExpressionLegend', '');
        return;
      }
      this.computedRNAlevels = {};
      let RNAlevels = null;
      if (this.mode === 'single') {
        console.log('compute single', Object.keys(this.firstRNAlevels).length, Object.keys(this.secondRNAlevels).length);
        RNAlevels = Object.keys(this.firstRNAlevels).length === 0 ? this.secondRNAlevels : this.firstRNAlevels;
        for (const enzID of Object.keys(RNAlevels)) {
          let level = Math.log2(RNAlevels[enzID] + 1);
          level = Math.round((level + 0.00001) * 100) / 100;
          this.computedRNAlevels[enzID] = [getSingleRNAExpressionColor(level), level];
        }
        this.computedRNAlevels['n/a'] = ['whitesmoke', 'n/a']; // fixme
        EventBus.$emit('updateRNAExpressionLegend', this.getSingleExpLvlLegend());
      } else {
        // comparison
        console.log('compute comparison', Object.keys(this.firstRNAlevels).length, Object.keys(this.secondRNAlevels).length);
        for (const enzID of Object.keys(this.firstRNAlevels)) {
          const log2tpm1 = Math.round((Math.log2(this.firstRNAlevels[enzID] + 1) + 0.00001) * 100) / 100;
          const log2tpm2 = Math.round((Math.log2(this.secondRNAlevels[enzID] + 1) + 0.00001) * 100) / 100;
          let level = Math.log2((this.secondRNAlevels[enzID] + 1) / (this.firstRNAlevels[enzID] + 1));
          level = Math.round((level + 0.00001) * 100) / 100;
          this.computedRNAlevels[enzID] = [getComparisonRNAExpressionColor(level), level, log2tpm1, log2tpm2];
        }
        this.computedRNAlevels['n/a'] = ['lightgray', 'n/a']; // fixme
        EventBus.$emit('updateRNAExpressionLegend', this.getComparisonExpLvlLegend());
      }
      this.$nextTick(() => {
        EventBus.$emit(this.dim === '2d' ? 'apply2DHPARNAlevels' : 'apply3DHPARNAlevels' , this.computedRNAlevels);
      });
    },
    getSingleExpLvlLegend,
    getComparisonExpLvlLegend,
  },
};
</script>

<style lang="scss"></style>
