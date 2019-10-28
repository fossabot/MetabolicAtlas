<template>
  <div>
    <div class="has-text-centered" :title="hoverTitleText">
      {{ title }}
      <span class="icon"><i class="fa fa-info-circle"></i></span>
    </div>
    <div class="fileSelectBut file is-centered">
      <label class="file-label">
        <input class="file-input" type="file" name="resume" @change="getFileName">
        <span class="file-cta">
          <span class="file-icon"><i class="fa fa-upload"></i></span>
          <span class="file-label">
            Choose a file ...
          </span>
        </span>
      </label>
    </div>
    <div v-if="fileName" class="fileNameBox">
      <div v-show="!showFileLoader" class="tags has-addons is-centered"
           :title="errorParsingFile ? errorParsingFileText : parsedInfoText">
        <span class="tag" :class="errorParsingFile ? 'is-danger' : 'is-success'">
          <div class="is-size-6">{{ fileName }}</div>
        </span>
        <a class="tag is-delete" title="Unload file" @click="unloadUploadedFile()"></a>
      </div>
      <div v-show="showFileLoader" class="has-text-centered">
        <a class="button is-small is-loading"></a>
      </div>
    </div>
  </div>
</template>

<script>

import { parseFiledata } from '@/helpers/file';

export default {
  name: 'FileLoaderPanel',
  props: {
    title: String,
    hoverTitleText: String,
  },
  data() {
    return {
      fileName: '',
      showFileLoader: false,

      errorParsingFile: false,
      errorParsingFileText: '',

      parsedInfo: {},
      parsedInfoText: '',
    };
  },
  methods: {
    getFileName(e) {
      if (e.target.files.length === 0) {
        this.fileName = '';
        // TODO reset PATH?
        return;
      }

      this.showFileLoader = true;
      this.errorParsingFile = false;
      this.errorParsingFileText = '';
      this.parsedInfo = {};
      const reader = new FileReader();

      // assigning handler
      reader.onloadend = (evt) => {
        this.parsedInfo = parseFiledata(evt.target.result);
        this.showFileLoader = false;
        if (this.parsedInfo.error) {
          this.errorParsingFile = true;
          this.errorParsingFileText = this.parsedInfo.error;
          this.$emit('errorParsingFile', this.errorParsingFileText);
          return;
        }

        this.fileName = e.target.files[0].name;
        this.parsedInfoText = `Entries found: ${this.parsedInfo.rowCount} - Columns parsed: ${this.parsedInfo.header.length}`;
        this.$emit('loadedFileData', this.parsedInfo);
      };

      // start reading
      reader.readAsText(e.target.files[0]);
    },
    unloadUploadedFile() {
      this.showFileLoader = false;
      this.errorParsingFile = false;
      this.errorParsingFileText = '';
      this.fileName = '';
      this.parsedInfo = {};
      this.$emit('unloadFileData');
    },
  },
};
</script>

<style lang="scss">
.fileSelectBut {
  margin-bottom: 0.5rem;
}

.fileNameBox {
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
</style>
