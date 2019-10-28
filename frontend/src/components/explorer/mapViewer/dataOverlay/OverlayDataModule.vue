<template>
  <div class="">
    <FileLoaderPanel v-if="panelData.fileLoader" :title="panelData.fileLoader.title"
                     :hover-title-text="panelData.fileLoader.hoverTitleText"
                     @loadedFileData="handleLoadedFileData" @unloadFileData="handleUnLoadedFileData">
    </FileLoaderPanel>

    <template v-for="(data, di) in panelData.dataPanels">
      <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
      <div class="card card-margin">
        <div class="card-content card-content-compact">
          <div class="has-text-centered title is-size-6">{{ data.name }}</div>
          <template v-for="(ds, i) in panelData.dataSources">
            <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
            <div class="control">
              <span v-html="ds.selectDescription"></span>
              <div class="select is-fullwidth">
                <select v-model="data.selectsForDataSources[ds.source].selectedValue"
                        :disabled="data.selectsForDataSources[ds.source].isDisabled
                          || (i === 0 ? isDisabledDataSource1 : isDisabledDataSource2)"
                        @change="applyData(di, i)">
                  <template v-if="i === 0"> <!-- loaded data on create (from DB)-->
                    <option v-if="ds.selectNoneOptionText">{{ ds.selectNoneOptionText }}</option>
                    <option v-for="col in ds.colNames" :key="`${col}-${di}-1`"
                            class="clickable is-capitalized">{{ col }}</option>
                  </template>
                  <template v-else> <!-- uploaded file data -->
                    <template v-if="hasSeriesDataSource2">
                      <option v-if="ds.selectNoneOptionText">{{ ds.selectNoneOptionText }}</option>
                    </template>
                    <template v-else>
                      <option>No file uploaded</option>
                    </template>
                  </template>
                  <option v-for="col in ds.colNames" :key="`${col}-${di}-2`"
                          class="clickable is-capitalized">{{ col }}</option>
                </select>
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>

    <template v-if="panelData.legend && (selectedData1 || selectedData2)">
      <Legend :text="panelData.legend[mode].text"
              :gradient="panelData.legend[mode].gradient"
              :left-value="panelData.legend[mode].leftValue"
              :right-value="panelData.legend[mode].rightValue"
              :nacolor="panelData.legend[mode].nacolor"
              :natext="panelData.legend[mode].natext">
      </Legend>
    </template>

    <DataProcessor
      ref="dataproc"
      :model="model"
      :map-type="mapType"
      :map-name="mapName"
      :dim="dim"
      :selected-data1="selectedData1"
      :selected-data2="selectedData2"
      :selected-data1-source="selectedData1Source"
      :selected-data2-source="selectedData2Source"
      :data-source1-cols="panelData.dataSources[0].colNames"
      :data-source2-cols="panelData.dataSources[1].colNames"
      :fetch-source1-data-function="panelData.dataProcessor.fetchSource1DataFunction"
      :parse-source1-data-function="panelData.dataProcessor.parseSource1DataFunction"
      :parse-source2-data-function="panelData.dataProcessor.parseSource2DataFunction"
      :compute-data-function="panelData.dataProcessor.computeDataFunction"
      :mode="mode"
      :loaded-file-data="loadedFileData">
    </DataProcessor>
  </div>
</template>

<script>
import Vue from 'vue';
import DataProcessor from './DataProcessor.vue';
import Legend from '@/components/explorer/mapViewer/Legend.vue';
import FileLoaderPanel from '@/components/explorer/mapViewer/dataOverlay/FileLoaderPanel.vue';
import { default as EventBus } from '@/event-bus';

const NOFILELOADED = 'No file uploaded';

export default {
  name: 'OverlayDataModule',
  components: {
    FileLoaderPanel,
    DataProcessor,
    Legend,
  },
  props: {
    model: Object,
    mapType: String,
    mapName: String,
    dim: String,
    panelData: Object,
  },
  data() {
    return {
      loadedFileData: null,
    };
  },
  computed: {
    isDisabledDataSource1() {
      return this.panelData.dataSources[0].colNames.length === 0;
    },
    isDisabledDataSource2() {
      return this.panelData.dataSources[1].colNames.length === 0;
    },
    hasSeriesDataSource2() {
      return !this.isDisabledDataSource2;
    },
    isSelectedData1Source1() {
      return this.panelData.dataSources[0].colNames.length !== 0
        && this.panelData.dataPanels[0].selectsForDataSources[this.panelData.dataSources[0].source]
          .selectedValue !== this.dataSource1NoneValue;
    },
    isSelectedData2Source1() {
      return this.panelData.dataSources[0].colNames.length !== 0
        && this.panelData.dataPanels[1].selectsForDataSources[this.panelData.dataSources[0].source]
          .selectedValue !== this.panelData.dataSources[0].selectNoneOptionText;
    },
    isSelectedData1Source2() {
      return !this.isDisabledDataSource2
        && !(NOFILELOADED, this.dataSource2NoneValue).includes(
          this.panelData.dataPanels[0].selectsForDataSources[this.panelData.dataSources[1].source].selectedValue);
    },
    isSelectedData2Source2() {
      return !this.isDisabledDataSource2
      && !(NOFILELOADED, this.dataSource2NoneValue).includes(
        this.panelData.dataPanels[1].selectsForDataSources[this.panelData.dataSources[1].source].selectedValue);
    },
    isSelectedData1() {
      return this.isSelectedData1Source1 || this.isSelectedData1Source2;
    },
    isSelectedData2() {
      return this.isSelectedData2Source1 || this.isSelectedData2Source2;
    },
    dataSource1NoneValue() {
      return this.panelData.dataSources[0].selectNoneOptionText;
    },
    dataSource2NoneValue() {
      return this.panelData.dataSources[1].selectNoneOptionText;
    },
    selectedData1Source() {
      return this.isSelectedData1Source1 ? 'NOT FILE' : 'FILE';
    },
    selectedData2Source() {
      return this.isSelectedData2Source1 ? 'NOT FILE' : 'FILE';
    },
    selectedData1() {
      if (this.isSelectedData1) {
        const index = this.isSelectedData1Source1 ? 0 : 1;
        return this.panelData.dataPanels[0]
          .selectsForDataSources[this.panelData.dataSources[index].source].selectedValue;
      }
      return '';
    },
    selectedData2() {
      if (this.isSelectedData2) {
        const index = this.isSelectedData2Source1 ? 0 : 1;
        return this.panelData.dataPanels[1]
          .selectsForDataSources[this.panelData.dataSources[index].source].selectedValue;
      }
      return '';
    },
    mode() {
      return this.selectedData1 && this.isSelectedData2 ? 'comparison' : 'single';
    },
  },
  mounted() {
    EventBus.$off('modulesComputeData');
    EventBus.$on('modulesComputeData', () => {
      Vue.nextTick(() => {
        this.$refs.dataproc.processData(true); // force to reupdate the map even if the selects didn't change
      });
    });
  },
  methods: {
    applyData(dataIndex, sourceIndex) {
      // reset the other <select> value if set
      if (dataIndex === 0 && sourceIndex === 0 && this.isSelectedData1Source2) {
        this.panelData.dataPanels[dataIndex].selectsForDataSources[this.panelData.dataSources[1].source]
          .selectedValue = this.dataSource2NoneValue;
      } else if (dataIndex === 1 && sourceIndex === 0 && this.isSelectedData2Source2) {
        this.panelData.dataPanels[dataIndex].selectsForDataSources[this.panelData.dataSources[1].source]
          .selectedValue = this.dataSource2NoneValue;
      } else if (dataIndex === 0 && sourceIndex === 1 && this.isSelectedData1Source1) {
        this.panelData.dataPanels[dataIndex].selectsForDataSources[this.panelData.dataSources[0].source]
          .selectedValue = this.dataSource1NoneValue;
      } else if (dataIndex === 1 && sourceIndex === 1 && this.isSelectedData2Source1) {
        this.panelData.dataPanels[dataIndex].selectsForDataSources[this.panelData.dataSources[0].source]
          .selectedValue = this.dataSource1NoneValue;
      }

      // apply the selected values
      this.$nextTick(() => {
        this.$refs.dataproc.processData();
      });
    },
    handleLoadedFileData(data) {
      this.panelData.dataPanels[0].selectsForDataSources[this.panelData.dataSources[1].source]
        .selectedValue = this.dataSource2NoneValue;
      this.panelData.dataPanels[1].selectsForDataSources[this.panelData.dataSources[1].source]
        .selectedValue = this.dataSource2NoneValue;
      this.panelData.dataSources[1].colNames = data.header;
      this.loadedFileData = data.data; // :)
    },
    handleUnLoadedFileData() {
      this.panelData.dataSources[1].colNames = [];
      this.panelData.dataPanels[0].selectsForDataSources[this.panelData.dataSources[1].source]
        .selectedValue = NOFILELOADED;
      this.panelData.dataPanels[1].selectsForDataSources[this.panelData.dataSources[1].source]
        .selectedValue = NOFILELOADED;
      this.$nextTick(() => {
        this.$refs.dataproc.processData();
      });
    },
  },
};
</script>

<style lang="scss">
</style>
