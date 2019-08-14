<template></template>

<script>
import axios from 'axios';
import $ from 'jquery';
import { default as EventBus } from '../../../event-bus';
import { getRNAExpressionColor } from '../../../expression-sources/hpa';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'RNAexpression',
  props: ['model', 'mapType', 'mapName'],
  data() {
    return {
      errorMessage: '',
      HPATissue: [],
      HPARNAlevelsHistory: {},
      HPARNAlevels: {}, // enz id as key, current tissue level as value
    };
  },
  created() {
    EventBus.$off('load2DHPARNAlevels');
    EventBus.$off('load3DHPARNAlevels');

    EventBus.$on('load2DHPARNAlevels', (tissue) => {
      this.loadHPAlevelsOnMap(tissue, '2d');
    });

    EventBus.$on('load3DHPARNAlevels', (tissue) => {
      this.loadHPAlevelsOnMap(tissue, '3d');
    });

    this.getHPATissue();
  },
  methods: {
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
    loadHPAlevelsOnMap(tissue, dim) {
      if (this.mapName in this.HPARNAlevelsHistory && dim in this.HPARNAlevelsHistory[this.mapName]) {
        this.parseHPARNAlevels(tissue, dim);
        return;
      }
      axios.get(`${this.model.database_name}/gene/hpa_rna_levels/${this.mapType}/${dim}/${this.mapName}`)
      .then((response) => {
        if (!(this.mapName in this.HPARNAlevelsHistory)) {
          this.HPARNAlevelsHistory[this.mapName] = {};
        }
        this.HPARNAlevelsHistory[this.mapName][dim] = response.data;
        setTimeout(() => {
          this.parseHPARNAlevels(tissue, dim);
        }, 0);
      })
      .catch(() => {
        EventBus.$emit('loadRNAComplete', false, '');
        return;
      });
    },
    parseHPARNAlevels(tissue, dim) {
      if (tissue === 'None') {
        this.HPARNAlevels = {};
      } else {
        const index = this.HPARNAlevelsHistory[this.mapName][dim].tissues.indexOf(tissue);
        const levels = this.HPARNAlevelsHistory[this.mapName][dim].levels;
        for (const array of levels) {
          const enzID = array[0];
          let level = Math.log2(parseFloat(array[1].split(',')[index]) + 1);
          level = Math.round((level + 0.00001) * 100) / 100; // round value
          this.HPARNAlevels[enzID] = [level, getRNAExpressionColor(level)];
        }
      }
      EventBus.$emit(dim === '2d' ? 'apply2DHPARNAlevels' : 'apply3DHPARNAlevels' , this.HPARNAlevels);
    },
  },
};
</script>

<style lang="scss"></style>
