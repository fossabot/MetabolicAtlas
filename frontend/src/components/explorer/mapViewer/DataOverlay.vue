<template>
  <div class="column is-one-fifth-widescreen is-one-quarter-desktop
              is-one-quarter-tablet is-half-mobile has-background-lightgray"
       style="padding-left: 0; overflow-y: auto;">
    <div class="columns is-multiline">
      <template v-for="panel in panels">
        <!-- eslint-disable-next-line vue/valid-v-for -->
        <DataOverlayPanel
          :component="panel.componentName"
          :model="model"
          :map-type="mapType"
          :map-name="mapName"
          :dim="dim"
          :panel-data="panel">
        </DataOverlayPanel>
      </template>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import DataOverlayPanel from '@/components/explorer/mapViewer/dataOverlay/DataOverlayPanel.vue';
import { default as messages } from '../../../helpers/messages';
import { singleColors, notDetectedColor, getSingleRNAExpressionColor, getComparisonRNAExpressionColor, multipleColors } from '@/expression-sources/hpa';
import { default as EventBus } from '../../../event-bus';

export default {
  name: 'DataOverlay',
  components: {
    DataOverlayPanel,
  },
  props: {
    model: Object,
    mapType: String,
    mapName: String,
    dim: String,
  },
  data() {
    return {
      loadErrorMesssage: '',

      panels: [
        {
          componentName: 'GeneExpression',
          buttonTitle: 'Gene expression data',
          title: 'Gene expression data',
          dataPanels: [
            {
              name: 'Data1',
              selectsForDataSources: {
                HPA: {
                  isDisabled: false,
                  selectedValue: 'None',
                },
                File: {
                  isDisabled: false,
                  selectedValue: 'No file uploaded',
                },
              },
            }, {
              name: 'Data2 (for comparison)',
              selectsForDataSources: {
                HPA: {
                  isDisabled: false,
                  selectedValue: 'None',
                },
                File: {
                  isDisabled: false,
                  selectedValue: 'No file uploaded',
                },
              },
            },
          ],
          dataSources: [
            {
              source: 'HPA',
              selectDescription: 'RNA levels from <a href="https://www.proteinatlas.org" target="_blank">proteinAtlas.org</a>',
              selectNoneOptionText: 'None',
              colNames: [],
            }, {
              source: 'File',
              selectDescription: 'Or uploaded file',
              selectNoneOptionText: 'None',
              colNames: [],
            },
          ],
          legend: {
            single: {
              text: 'log<sub>2</sub>(TPM+1)',
              gradient: `${singleColors}`,
              leftValue: '0',
              rightValue: '7+',
              nacolor: `${notDetectedColor}`,
              natext: 'n/a',
            },
            comparison: {
              text: 'log<sub>2</sub>(TPM<sub>T2</sub>+1 / TPM<sub>T1</sub>+1)',
              gradient: `${multipleColors}`,
              leftValue: '-5',
              rightValue: '5',
              nacolor: `${notDetectedColor}`,
              natext: 'n/a',
            },
          },
          fileLoader: {
            title: 'Load custom gene expression data',
            hoverTitleText: 'Load a TSV file with gene IDs and TPM values. More information can be found in the documentation.',
          },
          dataProcessor: {
            fetchSource1DataFunction: null,
            parseSource1DataFunction: null,
            parseSource2DataFunction: null,
            computeDataFunction: null,
          },
        }],
    };
  },
  created() {
    // GENE EXPRESSION DATA
    this.getColNames(`${this.model.database_name}/gene/hpa_tissue/`, 'GeneExpression');
    this.panels[0].dataProcessor.fetchSource1DataFunction = this.fetchGeneExpLevels;
    this.panels[0].dataProcessor.parseSource1DataFunction = this.parseGeneExpDBLevels;
    this.panels[0].dataProcessor.parseSource2DataFunction = this.parseGeneExpFileLevels;
    this.panels[0].dataProcessor.computeDataFunction = this.computeGeneExpLevels;

    // REACTION FLUXES DATA
    // indexPanel = 1;
    // METABOLITE DATA
    // indexPanel = 2;
  },
  methods: {
    /* eslint-disable no-param-reassign */
    getColNames(url, componentName) {
      this.panels.every((panel) => {
        if (panel.componentName === componentName) {
          axios.get(url)
            .then((response) => {
              panel.dataSources[0].colNames = response.data;
            })
            .catch((error) => {
              switch (error.response.status) {
                default:
                  this.loadErrorMesssage = messages.unknownError;
              }
            });
          return false;
        }
        return true;
      });
    },
    fetchGeneExpLevels(params) {
      // params { 4 keys
      //   colNames = list of tissues fetched from the backend
      //   selectedCol = current select tissue to show on the map, not usefull here, all tissues are retrieved at one from the db
      //   destination = var to store the parsed data
      // }
      return axios.get(`${this.model.database_name}/gene/hpa_rna_levels/${this.mapType}/${this.dim}/${this.mapName}`)
        .then((response) => {
          params.destination = response.data;
          // this.$emit('parseFetchedData', params); // always include this line
        });
    },
    parseGeneExpDBLevels(params) {
      // params { 5 keys
      //   fetchedData = data fetched from the backend
      //   colNames = list of tissues fetched from the backend
      //   selectedCol = current select tissue to show on the map
      //   destination = var to store the parsed data
      // }
      params.destination = {};
      const tissueIndex = params.colNames.indexOf(params.selectedCol);
      const { levels } = params.fetchedData;
      levels.forEach((array) => {
        const enzID = array[0];
        const level = parseFloat(array[1].split(',')[tissueIndex]);
        params.destination[enzID] = level;
      });
      params.destination['n/a'] = 'n/a';
    },
    parseGeneExpFileLevels(params) {
      // params { 5 keys
      //   fetchedData = data fetched from the backend
      //   colNames = list of tissues fetched from the backend
      //   selectedCol = current select tissue to show on the map
      //   destination = var to store the parsed data
      // }
      params.destination = params.fetchedData[params.selectedCol];
      params.destination['n/a'] = 'n/a';
    },
    computeGeneExpLevels(params) {
      // params { 8 keys
      //   selectedData1Col
      //   selectedData2Col
      //   selectedData1Source
      //   selectedData2Source
      //   data1ValuesDict
      //   data2ValuesDict
      //   mode = single / comparison
      //   destination
      // }
      // the generic compute function in the DataProcess do not trigger anything
      // and event must be send at the end the this function
      //  with the result data computed, to the Map Viewer component
      if (Object.keys(params.data1ValuesDict).length === 0 && Object.keys(params.data2ValuesDict).length === 0) {
        // nothing to compute
        EventBus.$emit(this.dim === '2d' ? 'apply2DGeneExplevels' : 'apply3DGeneExplevels', {});
        return;
      }
      params.destination = {};
      let RNAlevels = null;
      if (params.mode === 'single') {
        RNAlevels = Object.keys(params.data1ValuesDict).length === 0
          ? params.data2ValuesDict : params.data1ValuesDict;
        Object.keys(RNAlevels).forEach((enzID) => {
          const level = this.roundValue(Math.log2(RNAlevels[enzID] + 1));
          params.destination[enzID] = [getSingleRNAExpressionColor(level), level];
        });
        params.destination['n/a'] = [getSingleRNAExpressionColor(NaN), 'n/a'];
      } else {
        // comparison
        if (params.selectedData1Source === 'HPA' && params.selectedData1Source === params.selectedData2Source) {
          // HPA tissues data have the same entries, so no need to check for missing geneID
          Object.keys(params.data1ValuesDict).forEach((enzID) => {
            const log2tpm1 = this.roundValue(Math.log2(params.data1ValuesDict[enzID] + 1));
            const log2tpm2 = this.roundValue(Math.log2(params.data2ValuesDict[enzID] + 1));
            const level = this.roundValue(
              Math.log2((params.data2ValuesDict[enzID] + 1) / (params.data1ValuesDict[enzID] + 1))
            );
            params.destination[enzID] = [getComparisonRNAExpressionColor(level), level, log2tpm1, log2tpm2];
          });
        } else {
          // HPA/custom file comparison or custom/custom comparison
          Object.keys(params.data1ValuesDict).forEach((enzID) => {
            const log2tpm1 = this.roundValue(Math.log2(params.data1ValuesDict[enzID] + 1));
            if (enzID in params.data2ValuesDict) {
              const log2tpm2 = this.roundValue(Math.log2(params.data2ValuesDict[enzID] + 1));
              const level = this.roundValue(
                Math.log2((params.data2ValuesDict[enzID] + 1) / (params.data1ValuesDict[enzID] + 1))
              );
              params.destination[enzID] = [getComparisonRNAExpressionColor(level), level, log2tpm1, log2tpm2];
            } else {
              params.destination[enzID] = [getComparisonRNAExpressionColor(NaN), 'n/a', log2tpm1, 'n/a'];
            }
          });
          Object.keys(params.data2ValuesDict)
            .filter(enzID => !(enzID in params.data1ValuesDict))
            .forEach((enzID) => {
              const log2tpm2 = this.roundValue(Math.log2(params.data2ValuesDict[enzID] + 1));
              params.destination[enzID] = [getComparisonRNAExpressionColor(NaN), 'n/a', 'n/a', log2tpm2];
            });
        }
        params.destination['n/a'] = [getComparisonRNAExpressionColor(NaN), 'n/a'];
      }
      this.$nextTick(() => {
        EventBus.$emit(this.dim === '2d' ? 'apply2DGeneExplevels' : 'apply3DGeneExplevels', params.destination);
      });
    },
    roundValue(value) {
      return Math.round((value + 0.00001) * 100) / 100;
    },
  },
};
</script>

<style lang="scss">
</style>
