<template>
  <section class="section section-no-top extended-section">
    <div class="container">
      <div v-if="errorMessage">
        {{ errorMessage }}
      </div>
      <div v-else>
        <h2 class="title is-2">Integrated GEMs</h2>
        <p class="is-size-5">
          These models are integrated into the Metabolic Atlas database; they can be explored via {{ messages.gemBrowserName }}, {{ messages.mapViewerName }} and {{ messages.interPartName }}.
        </p><br><br>
        <div id="integrated" class="columns is-multiline is-variable is-6">
          <div class="column is-half" v-for="model in integratedModels">
            <div class="card is-size-5">
              <header class="card-header clickable has-background-primary-lighter" @click="showIntegratedModelData(model)">
                <p class="card-header-title card-content has-text-weight-bold has-text-primary">
                  {{ model.short_name }} &ndash; {{ model.full_name }}
                </p>
                <div class="card-header-icon">
                  <span class="icon has-text-primary">
                    <i class="fa fa-plus-square"></i>
                  </span>
                </div>
              </header>
              <div class="card-content is-fullheight">
                <div class="columns">
                  <div class="column">
                    Reactions: {{ model.reaction_count }}<br>
                    Metabolites: {{ model.metabolite_count }}<br>
                    Enzymes: {{ model.enzyme_count }}<br>
                  </div>
                  <div class="column">
                    Date: {{ model.date || "n/a" }}<br>
                    <a :href="model.link" target="_blank">
                      <template v-if="model.link.includes('github.com')">
                        <span class="icon"><i class="fa fa-github"></i></span>
                        GitHub
                      </template>
                     <template v-else>
                        <span class="icon"><i class="fa fa-link fa-lg"></i></span>
                        External link
                     </template>
                    </a>
                  </div>
                </div>
              </div>
              <footer class="card-footer">
                <router-link class="card-footer-item is-info is-outlined" :to="{ path: `/explore/gem-browser/${model.database_name}` }">
                  <span class="icon is-large"><i class="fa fa-database fa-lg"></i></span>
                  <span>{{ messages.gemBrowserName }}</span>
                </router-link>
                <router-link class="card-footer-item is-info is-outlined" :to="{ path: `/explore/map-viewer/${model.database_name}` }">
                  <span class="icon is-large"><i class="fa fa-map-o fa-lg"></i></span>
                  <span>{{ messages.mapViewerName }}</span>
                </router-link>
              </footer>
            </div>
          </div>
        </div>
        <h2 class="title is-2">Repository</h2>
        <p class="is-size-5">While we do not provide support for these models, we are making them available to download. For support, the authors should be contacted. They are listed in the <i>References</i> section of each model. Click on any row to view more. To download multiple models at once use the <router-link :to=" { path: '/documentation', hash: 'FTP-download'} ">FTP server</router-link>.</p><br>
        <loader v-show="showLoader"></loader>
        <div v-if="GEMS.length != 0">
          <vue-good-table
            :columns="columns" :rows="GEMS"
            :sort-options="{ enabled: true }" styleClass="vgt-table striped bordered" :paginationOptions="tablePaginationOpts"
            @on-row-click="getModel">
          </vue-good-table>
        </div>
        <div v-else>
          <span v-if="!showLoader">No models available</span>
        </div>
        <br>
        <div id="gem-list-modal" class="modal" v-bind:class="{ 'is-active': showModelTable }">
          <div class="modal-background" @click="showModelTable = false"></div>
          <div class="modal-content column is-6-fullhd is-8-desktop is-10-tablet is-full-mobile has-background-white" v-on:keyup.esc="showModelTable = false" tabindex="0">
            <div id="modal-info" class="model-table">
              <h2 class="title">
                <template v-if="selectedModel.database_name">
                  {{ selectedModel.full_name }}
                </template>
                <template v-else>
                   <template v-if="selectedModel.tag || selectedModel.tissue || selectedModel.cell_type || selectedModel.cell_line">
                    {{ selectedModel.set_name }} - {{ selectedModel.tag || selectedModel.tissue || selectedModel.cell_type || selectedModel.cell_line }}
                   </template>
                   <template v-else>
                    {{ selectedModel.set_name }}
                   </template>
                </template>
              </h2>
              {{ selectedModel.description }}<br><br>
              <table class="table main-table">
                <tbody>
                  <tr v-for="field in model_fields">
                    <template v-if="['reaction_count', 'metabolite_count', 'enzyme_count'].includes(field.name)">
                      <td v-html="field.display" class="td-key has-background-primary has-text-white-bis"></td>
                      <td>{{ selectedModel[field.name] !== null ? selectedModel[field.name] : '-' }}</td>
                    </template>
                    <template v-else-if="typeof(selectedModel[field.name]) === 'boolean'">
                      <td v-html="field.display" class="td-key has-background-primary has-text-white-bis"></td>
                      <td>{{ selectedModel[field.name] ? 'Yes' : 'No' }}</td>
                    </template>
                    <template v-else-if="selectedModel[field.name]">
                      <td v-html="field.display" class="td-key has-background-primary has-text-white-bis"></td>
                      <td>{{ selectedModel[field.name] }}</td>
                    </template>
                  </tr>
                  <template v-if="selectedModel.authors && selectedModel.authors.length !== 0">
                    <tr v-for="a in selectedModel.authors">
                      <td class="td-key has-background-primary has-text-white-bis" :rowspan="selectedModel.authors.length">Author(s)
                      </td>
                      <td>
                        {{ a.given_name }} {{ a.family_name }}
                      </td>
                    </tr>
                  </template>
                  <tr v-if="selectedModel.date">
                    <td  class="td-key has-background-primary has-text-white-bis">Date</td>
                    <td>
                      {{ selectedModel.date }}
                    </td>
                  </tr>
                  <tr v-if="selectedModel.link">
                    <td class="td-key has-background-primary has-text-white-bis">URL</td>
                    <td>
                      {{ selectedModel.link }}
                    </td>
                  </tr>
                  <tr v-if="selectedModel.ref && selectedModel.ref.length !== 0">
                    <td class="td-key has-background-primary has-text-white-bis">Reference(s)</td>
                    <td>
                      <template v-for="oneRef in selectedModel.ref">
                        <p v-if="!oneRef.link">{{ oneRef.title }}</p>
                        <a v-else :href="oneRef.link" target="_blank">
                          {{ oneRef.title }} (PMID: {{ oneRef.pmid }})
                        </a>
                        <br>
                      </template>
                    </td>
                  </tr>
                </tbody>
              </table>
              <template v-if="selectedModel.files">
                <br>
                <span class="subtitle">Files</span>
                <table class="table">
                  <tbody>
                    <tr>
                      <td v-for="file in selectedModel.files">
                        <a :href="`${filesURL}${file.path}`">{{ file.format }}</a>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </template>
            </div>
          </div>
          <button class="modal-close is-large" @click="showModelTable = false"></button>
        </div>
      </div>
    </div>
  </section>
</template>


<script>
import axios from 'axios';
import $ from 'jquery';
import { VueGoodTable } from 'vue-good-table';
import 'vue-good-table/dist/vue-good-table.css';
import Loader from 'components/Loader';
import { default as EventBus } from '../event-bus';
import { default as messages } from '../helpers/messages';

export default {
  name: 'repository',
  components: {
    Loader,
    VueGoodTable,
  },
  data() {
    return {
      columns: [
        {
          label: 'Set',
          field: 'set_name',
          filterOptions: {
            enabled: true,
            filterDropdownItems: [],
            filterFn: (a, b) => a === b,
          },
          sortable: true,
        }, {
          label: 'Organism',
          field: 'organism',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
          html: true,
        }, {
          label: 'Tag',
          field: 'tag',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: 'System/Organ',
          field: 'organ_system',
          filterOptions: {
            enabled: true,
            filterDropdownItems: [],
            filterFn: (a, b) => a === b,
          },
          sortable: true,
        }, {
          label: 'Condition',
          field: 'condition',
          filterOptions: {
            enabled: true,
            filterDropdownItems: [],
            filterFn: (a, b) => a === b,
          },
          sortable: true,
        }, {
          label: 'Tissue/Cell type',
          field: 'tissue',
          filterOptions: {
            enabled: true,
            filterFn: (a, b) => a.toLowerCase().includes(b.toLowerCase().trim()),
          },
          sortable: true,
        }, {
          label: 'Stats',
          field: 'stats',
          sortable: false,
          html: true,
        }, {
          label: 'Latest publication',
          field: 'year',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: 'Maintained',
          field: 'maintained',
          filterOptions: {
            enabled: true,
            filterDropdownItems: ['Yes', 'No'],
          },
          sortable: true,
        },
      ],
      model_fields: [
        { name: 'version', display: 'Version' },
        { name: 'organism', display: 'Organism' },
        { name: 'set_name', display: 'Set' },
        { name: 'organ_system', display: 'System' },
        { name: 'condition', display: 'Condition' },
        { name: 'tissue', display: 'Tissue' },
        { name: 'cell_type', display: 'Cell&nbsp;type' },
        { name: 'cell_line', display: 'Cell&nbsp;line' },
        { name: 'reaction_count', display: 'Reactions' },
        { name: 'metabolite_count', display: 'Metabolites' },
        { name: 'enzyme_count', display: 'Enzymes/genes' },
        { name: 'year', display: 'Year' },
        { name: 'maintained', display: 'Maintained' },
      ],
      selectedModel: {},
      errorMessage: '',
      GEMS: [],
      showModelTable: false,
      showLoader: false,
      tablePaginationOpts: {
        enabled: true,
        perPage: 50,
        position: 'both',
        perPageDropdown: [25, 50, 100, 200],
        dropdownAllowAll: false,
        setCurrentPage: 1,
        nextLabel: 'next',
        prevLabel: 'prev',
        rowsPerPageLabel: 'Rows per page',
        ofLabel: 'of',
      },
      messages,
      integratedModels: [],
      filesURL: 'https://ftp.metabolicatlas.org/',
    };
  },
  created() {
    EventBus.$on('viewGem', (modelID) => {
      this.getModelData(modelID);
    });
  },
  beforeMount() {
    this.getIntegratedModels();
    this.getModels();
  },
  methods: {
    getIntegratedModels() {
      // get models list
      axios.get('models/')
      .then((response) => {
        const models = [];
        for (const model of response.data) {
          $.extend(model, model.sample);
          model.sample = [model.sample.tissue, model.sample.cell_type, model.sample.cell_line].filter(e => e).join(' ‒ ') || '-';
          models.push(model);
        }
        models.sort((a, b) => (a.short_name.toLowerCase() < b.short_name.toLowerCase() ? -1 : 1));
        this.integratedModels = models;
      })
      .catch(() => {
        this.errorMessage = messages.unknownError;
      });
    },
    getModel(params) {
      this.getModelData(params.row.id);
    },
    getModelData(id) {
      axios.get(`gems/${id}`)
      .then((response) => {
        const model = response.data;
        // reformat the dictionnary
        delete model.id;
        $.extend(model, model.sample);
        delete model.sample;
        const setDescription = model.gemodelset.description;
        delete model.gemodelset.description;
        model.gemodelset.set_name = model.gemodelset.name;
        delete model.gemodelset.name;
        if (model.ref.length === 0) {
          model.ref = model.gemodelset.reference;
        }
        delete model.gemodelset.reference;
        $.extend(model, model.gemodelset);
        delete model.gemodelset;
        if (!model.description) {
          model.description = setDescription;
        }

        this.selectedModel = model;
        this.showModelTable = true;
      })
      .catch(() => {
        this.showModelTable = false;
      });
    },
    showIntegratedModelData(model) {
      this.selectedModel = model;
      this.showModelTable = true;
    },
    getModels() {
      this.showLoader = true;
      axios.get('gems/')
      .then((response) => {
        this.GEMS = [];
        const setDropDownFilter = new Set();
        const systemDropDownFilter = new Set();
        const conditionDropDownFilter = new Set();
        for (let i = 0; i < response.data.length; i += 1) {
          const gem = response.data[i];
          const sample = gem.sample;
          delete gem.sample;
          const gemex = $.extend(gem, sample);
          gemex.tissue = [gemex.tissue, gemex.cell_type, gemex.cell_line].filter(e => e).join(' ‒ ') || '-';
          delete gemex.cell_type;
          gemex.stats = `reactions:&nbsp;${gem.reaction_count}<br>metabolites:&nbsp;${gemex.metabolite_count}<br>enzymes:&nbsp;${gemex.enzyme_count}`;
          delete gemex.reaction_count; delete gemex.enzyme_count; delete gemex.metabolite_count;
          gemex.maintained = gem.maintained ? 'Yes' : 'No';
          gemex.organ_system = gemex.organ_system || '-';
          gemex.condition = gemex.condition || '-';
          this.GEMS.push(gemex);

          // setup filters
          setDropDownFilter.add(gemex.set_name);
          systemDropDownFilter.add(gemex.organ_system);
          conditionDropDownFilter.add(gemex.condition);
        }
        this.columns[0].filterOptions.filterDropdownItems = Array.from(setDropDownFilter).sort();
        this.columns[3].filterOptions.filterDropdownItems = Array.from(systemDropDownFilter).sort();
        this.columns[4].filterOptions.filterDropdownItems =
          Array.from(conditionDropDownFilter).sort();

        this.errorMessage = '';
        this.showLoader = false;
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
        this.showLoader = false;
      });
    },
  },
};

</script>

<style lang="scss"></style>