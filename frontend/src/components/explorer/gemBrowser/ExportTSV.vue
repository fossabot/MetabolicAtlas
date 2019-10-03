<template>
  <a class="button is-primary"
     @click="exportToTSV">
    <span class="icon is-large"><i class="fa fa-download"></i></span>
    <span>Export to TSV</span>
  </a>
</template>

<script>

import { default as FileSaver } from 'file-saver';
import { default as EventBus } from '../../../event-bus';

export default {
  name: 'ExportTSV',
  props: {
    arg: [Number, String, Object, Array],
    filename: String,
    formatFunction: Function,
  },
  data() {
    return {
    };
  },
  methods: {
    exportToTSV() {
      try {
        let tsvContent = null;
        // one argument can be passed to the format function
        if (this.arg !== undefined) {
          tsvContent = this.formatFunction(this.arg);
        } else {
          tsvContent = this.formatFunction();
        }
        const blob = new Blob([tsvContent], {
          type: 'text/tsv;charset=utf-8',
        });
        FileSaver.saveAs(blob, this.filename);
      } catch (error) {
        console.log(error);
        EventBus.$emit('exportToTSVError', error);
      }
    },
  },
};
</script>

<style lang="scss"></style>
