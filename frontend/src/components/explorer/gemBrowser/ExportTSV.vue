<template>
  <a class="button is-primary" @click="exportToTSV">
    <span class="icon is-large"><i class="fa fa-download"></i></span>
    <span>Export to TSV</span>
  </a>
</template>

<script>

import { default as FileSaver } from 'file-saver';

export default {
  name: 'ExportTSV',
  props: {
    arg: [Number, String, Object, Array],
    filename: String,
    formatFunction: Function,
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
        this.props.filename = 'error';
      }
    },
  },
};
</script>

<style lang="scss"></style>
