<template>
  <div class="column">
    <div class="title is-size-4 has-text-centered">Reaction fluxes data</div>
    <div class="has-text-centered"
         title="Load a TSV file.">
      Load fluxes data<span class="icon"><i class="fa fa-info-circle"></i></span>
    </div>
    <div id="fileSelectBut" class="file is-centered">
      <label class="file-label">
        <input class="file-input"
               type="file"
               name="resume"
               @change="getFileName">
        <span class="file-cta">
          <span class="file-icon">
            <i class="fa fa-upload"></i>
          </span>
          <span class="file-label">
            Choose a file
          </span>
        </span>
      </label>
    </div>
    <div v-if="customFileName" id="fileNameBox">
      <div v-show="!showFileLoader" class="tags has-addons is-centered"
           :title="errorCustomFile ? errorCustomFileMsg : customFileInfo">
        <span class="tag" :class="errorCustomFile ? 'is-danger' : 'is-success'">
          <div class="is-size-6">{{ customFileName }}</div>
        </span>
        <a class="tag is-delete" title="Unload file" @click="unloadUploadedFile()"></a>
      </div>
      <div v-show="showFileLoader" class="has-text-centered">
        <a class="button is-small is-loading"></a>
      </div>
    </div>
    <div class="card card-margin">
      <div class="card-content card-content-compact">
        <div class="has-text-centered title is-size-6">Data 1</div>
        <div class="control">
          <p>data 1 description</p>
          <div class="select is-fullwidth">
            <select v-model="data1Value">
              <option>None</option>
              <!-- <option v-for="tissue in HPATissues" :key="tissue"
                      class="clickable is-capitalized">{{ tissue }}</option> -->
            </select>
          </div>
        </div>
      </div>
    </div>
    <div class="card card-margin">
      <div class="card-content card-content-compact">
        <div class="has-text-centered title is-size-6">Data 2 (for comparison)</div>
        <div class="control">
          <p>data 2 description</p>
          <div class="select is-fullwidth">
            <select v-model="data2Value">
              <option>None</option>
              <!-- <option v-for="tissue in HPATissues" :key="tissue"
                      class="clickable is-capitalized">{{ tissue }}</option> -->
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import { default as EventBus } from '../../../../event-bus';

// const NOFILELOADED = 'No file loaded';

export default {
  name: 'ReactionFluxes',
  components: {
  },
  props: {
    model: Object,
    mapType: String,
    mapName: String,
    dim: String,
  },
  data() {
    return {
      errorMessage: '',

      // customTissues: [NOFILELOADED],

      data1Value: 'None',
      data2Value: 'None',

      // tissue1Source: '',
      // tissue2Source: '',

      customFileName: '',
      showFileLoader: true,
      errorCustomFile: false,
      errorCustomFileMsg: '',
      customFileInfo: '',
    };
  },
  computed: {
  },
  created() {
  },
  methods: {
    getFileName(e) {
      if (e.target.files.length !== 0) {
        this.customFileName = e.target.files[0].name;
        this.errorCustomFile = false;
        this.errorCustomFileMsg = '';
        this.customFileInfo = '';
      } else {
        this.customFileName = '';
      }
    },
    unloadUploadedFile() {
      this.customFileName = '';
    },
    handleErrorCustomFile(errorMsg) {
      this.errorCustomFile = true;
      this.errorCustomFileMsg = errorMsg;
      this.showFileLoader = false;
    },
  },
};
</script>

<style lang="scss">

#fileSelectBut {
  margin-bottom: 0.5rem;
}

#fileNameBox {
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
