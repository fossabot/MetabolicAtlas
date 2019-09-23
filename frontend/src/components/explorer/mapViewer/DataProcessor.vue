<template>
  <div v-if="false">
  </div>
</template>

<script>

export default {
  name: 'DataProcessor',
  props: {
    model: Object,
    mapType: String,
    mapName: String,
    dim: String,
    selectedData1: String,
    selectedData2: String,
    selectedData1Source: String,
    selectedData2Source: String,
    dataSource1Cols: Array,
    dataSource2Cols: Array,
    fetchSource1DataFunction: Function,
    parseSource1DataFunction: Function,
    parseSource2DataFunction: Function,
    computeDataFunction: Function,
    mode: String,
    loadedFileData: Object, // correspond to fetchSource2Data
  },
  data() {
    return {
      errorMessage: '',

      currentSelectedData1: null,
      currentSelectedData2: null,
      currentSelectedData1Source: null,
      currentSelectedData2Source: null,

      dataSource1History: {},
      // dataSource2History: {},

      fetchSource1Data: null,

      parsedSource1Data: null,
      parsedSource2Data: null,

      data1ValuesDict: {},
      data2ValuesDict: {},

      computedDataValues: {},
    };
  },
  computed: {
    fetchSource2Data() {
      return this.loadedFileData;
    },
  },
  methods: {
    processData(forceCompute) {
      // limitation:
      // only 2 types of data source
      // source1 in from a axios promise
      // source2 in from the file uploaded and provide as prop
      if (!forceCompute
          && this.currentSelectedData1 === this.selectedData1
          && this.currentSelectedData2 === this.selectedData2
          && this.currentSelectedData1Source === this.selectedData1Source
          && this.currentSelectedData2Source === this.selectedData2Source) {
        return;
      }

      if (!this.selectedData1 && !this.selectedData2) {
        this.data1ValuesDict = {};
        this.data2ValuesDict = {};
        this.computeData();
      } else if (!this.selectedData1 && this.selectedData2) {
        this.data1ValuesDict = {};
        if (this.selectedData2Source !== 'FILE') {
          this.fetchSource1Function(this.selectedData2, () => {
            this.data2ValuesDict = this.parseSource1Data(this.selectedData2);
            this.computeData();
          });
        } else {
          this.data2ValuesDict = this.parseSource2Data(this.selectedData2);
          this.computeData();
        }
      } else if (this.selectedData1 && !this.selectedData2) {
        this.data2ValuesDict = {};
        if (this.selectedData1Source !== 'FILE') {
          this.fetchSource1Function(this.selectedData1, () => {
            this.data1ValuesDict = this.parseSource1Data(this.selectedData1);
            this.computeData();
          });
        } else {
          this.data1ValuesDict = this.parseSource2Data(this.selectedData1);
          this.computeData();
        }
      } else if (this.selectedData1 && this.selectedData2) {
        if (this.selectedData1Source === 'FILE') {
          if (this.selectedData2Source === 'FILE') {
            // both from the uploaded file
            this.data1ValuesDict = this.parseSource2Data(this.selectedData1);
            this.data2ValuesDict = this.parseSource2Data(this.selectedData2);
            this.computeData();
          } else {
            // data2 from db / data1 from file
            this.fetchSource1Function(this.selectedData2, () => {
              this.data1ValuesDict = this.parseSource2Data(this.selectedData1);
              this.data2ValuesDict = this.parseSource1Data(this.selectedData2);
              this.computeData();
            });
          }
        } else if (this.selectedData2Source === 'FILE') {
          // data1 from db / data2 from file
          this.fetchSource1Function(this.selectedData1, () => {
            this.data1ValuesDict = this.parseSource1Data(this.selectedData1);
            this.data2ValuesDict = this.parseSource2Data(this.selectedData2);
            this.computeData();
          });
        } else {
          this.fetchSource1Function(this.selectedData1, () => {
            this.data1ValuesDict = this.parseSource1Data(this.selectedData1);
            this.fetchSource1Function(this.selectedData2, () => {
              this.data2ValuesDict = this.parseSource1Data(this.selectedData2);
              this.computeData();
            });
          });
        }
      }

      this.currentSelectedData1 = this.selectedData1;
      this.currentSelectedData2 = this.selectedData2;
      this.currentSelectedData1Source = this.selectedData1Source;
      this.currentSelectedData2Source = this.selectedData2Source;
    },
    fetchSource1Function(selectedData, callback) {
      if (this.fetchSource1DataFromHistory()) {
        callback();
        return;
      }
      const params = {
        colNames: this.data1Cols,
        selectedCol: selectedData,
        destination: null,
      };
      this.fetchSource1DataFunction(params)
        .then(() => {
          // store the values in the history dict
          // limitation: 'selectedData' is not use in the history
          // might be needed depending how the data are stored in the db
          this.fetchSource1Data = params.destination;
          if (!(this.mapType in this.dataSource1History)) {
            this.dataSource1History[this.mapType] = {};
          }
          if (!(this.mapName in this.dataSource1History[this.mapType])) {
            this.dataSource1History[this.mapType][this.mapName] = {};
          }
          if (!(this.dim in this.dataSource1History[this.mapType][this.mapName])) {
            this.dataSource1History[this.mapType][this.mapName][this.dim] = {};
          }
          this.dataSource1History[this.mapType][this.mapName][this.dim] = this.fetchSource1Data;
          callback();
        });
    },
    parseSource1Data(selectedData) {
      const params = {
        fetchedData: this.fetchSource1Data,
        colNames: this.dataSource1Cols,
        selectedCol: selectedData,
        destination: null,
      };
      this.parseSource1DataFunction(params);
      return params.destination;
    },
    parseSource2Data(selectedData) {
      const params = {
        fetchedData: this.fetchSource2Data,
        colNames: this.dataSource2Cols,
        selectedCol: selectedData,
        destination: null,
      };
      this.parseSource2DataFunction(params);
      return params.destination;
    },
    computeData() {
      const params = {
        selectedData1Col: this.selectedData1,
        selectedData2Col: this.selectedData2,
        selectedData1Source: this.selectedData1Source,
        selectedData2Source: this.selectedData2Source,
        data1ValuesDict: this.data1ValuesDict,
        data2ValuesDict: this.data2ValuesDict,
        mode: this.mode,
        destination: null,
      };
      this.computeDataFunction(params);
      this.computedDataValues = params.destination;
    },
    fetchSource1DataFromHistory() {
      if (this.mapType in this.dataSource1History
        && this.mapName in this.dataSource1History[this.mapType]
        && this.dim in this.dataSource1History[this.mapType][this.mapName]) {
        this.fetchSource1Data = this.dataSource1History[this.mapType][this.mapName][this.dim];
        return true;
      }
      return false;
    },
  },
};
</script>

<style lang="scss"></style>
