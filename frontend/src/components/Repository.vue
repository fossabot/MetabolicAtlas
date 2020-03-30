<template>
  <section class="section section-no-top extended-section">
    <div class="container">
      <div v-if="errorMessage">
        {{ errorMessage }}
      </div>
      <div v-else>
        <h2 class="title is-2">Integrated GEMs</h2>
        <p class="is-size-5">
          These models are integrated into the Metabolic Atlas database;
          they can be explored via {{ messages.gemBrowserName }}, {{ messages.mapViewerName }} and
          {{ messages.interPartName }}.
        </p><br><br>
        <div id="integrated" class="columns is-multiline is-variable is-6">
          <div v-for="model in integratedModels" :key="model.short_name" class="column is-half">
            <div class="card is-size-5">
              <header class="card-header clickable has-background-primary-lighter"
                      @click="showIntegratedModelData(model)">
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
                    Genes: {{ model.gene_count }}<br>
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
                <router-link class="card-footer-item is-info is-outlined"
                             :to="{ name: 'browserRoot', params: { model: model.database_name } }">
                  <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
                  <span>{{ messages.gemBrowserName }}</span>
                </router-link>
                <router-link class="card-footer-item is-info is-outlined"
                             :to="{ path: `/explore/map-viewer/${model.database_name}` }">
                  <span class="icon is-large"><i class="fa fa-map-o fa-lg"></i></span>
                  <span>{{ messages.mapViewerName }}</span>
                </router-link>
              </footer>
            </div>
          </div>
        </div>
        <h2 class="title is-2">GEM Repository</h2>
        <p class="is-size-5">
          While we do not provide support for these models, we are making them available to download.
          For support, the authors should be contacted. They are listed in the <i>References</i> section of each model.
          Click on a row to display more information. To download multiple models at once use the
          <router-link :to=" { name: 'documentation', hash: 'FTP-download'} ">FTP server</router-link>.
        </p>
        <br>
        <loader v-show="showLoader"></loader>
        <div v-if="GEMS.length != 0">
          <vue-good-table :columns="columns" :rows="GEMS" :search-options="{ enabled: true, skipDiacritics: true }"
                          :sort-options="{ enabled: true }" style-class="vgt-table striped"
                          :pagination-options="tablePaginationOpts" @on-row-click="getModel">
          </vue-good-table>
        </div>
        <div v-else>
          <span v-if="!showLoader">No models available</span>
        </div>
        <br>
        <div v-if="showModelTable" id="gem-list-modal" class="modal is-active">
          <div class="modal-background" @click="showModelTable = false"></div>
          <div class="modal-content column is-6-fullhd is-8-desktop is-10-tablet is-full-mobile has-background-white"
               tabindex="0" @keyup.esc="showModelTable = false">
            <div id="modal-info" class="model-table">
              <h2 class="title">
                <template v-if="selectedModel.database_name">
                  {{ selectedModel.full_name }}
                </template>
                <template v-else>
                  {{ selectedModel.set_name }} -
                  {{ selectedModel.tag || selectedModel.tissue
                    || selectedModel.cell_type || selectedModel.cell_line || "" }}
                </template>
              </h2>
              {{ selectedModel.description }}<br><br>
              <table class="table main-table is-fullwidth">
                <tbody>
                  <tr v-for="field in model_fields" :key="field.name">
                    <template v-if="['reaction_count', 'metabolite_count', 'gene_count'].includes(field.name)">
                      <td class="td-key has-background-primary has-text-white-bis" v-html="field.display"></td>
                      <td>{{ selectedModel[field.name] !== null ? selectedModel[field.name] : '-' }}</td>
                    </template>
                    <template v-else-if="typeof(selectedModel[field.name]) === 'boolean'">
                      <td class="td-key has-background-primary has-text-white-bis" v-html="field.display"></td>
                      <td>{{ selectedModel[field.name] ? 'Yes' : 'No' }}</td>
                    </template>
                    <template v-else-if="selectedModel[field.name]">
                      <td class="td-key has-background-primary has-text-white-bis" v-html="field.display"></td>
                      <td>{{ selectedModel[field.name] }}</td>
                    </template>
                  </tr>
                  <tr v-if="selectedModel.authors && selectedModel.authors.length !== 0">
                    <td class="td-key has-background-primary has-text-white-bis">Author(s)</td>
                    <td>{{ selectedModel.authors.map(a => `${a.given_name} ${a.family_name}`).join(', ') }}</td>
                  </tr>
                  <tr v-if="selectedModel.date">
                    <td class="td-key has-background-primary has-text-white-bis">Date</td>
                    <td>{{ selectedModel.date }}</td>
                  </tr>
                  <tr v-if="selectedModel.link">
                    <td class="td-key has-background-primary has-text-white-bis">URL</td>
                    <td><a :href="selectedModel.link" target="_blank">{{ selectedModel.link }}</a></td>
                  </tr>
                </tbody>
              </table>
              <references :reference-list="referenceList" />
              <template v-if="selectedModel.files">
                <h4 class="title is-size-4">Files</h4>
                <template v-for="file in selectedModel.files">
                  <a :key="file.path" class="button" :href="`${filesURL}${file.path}`">{{ file.format }}</a>&nbsp;
                </template>
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
import Loader from '@/components/Loader';
import References from '@/components/shared/References';
import { default as EventBus } from '@/event-bus';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Repository',
  components: {
    Loader,
    VueGoodTable,
    References,
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
        { name: 'gene_count', display: 'Genes' },
        { name: 'year', display: 'Year' },
        { name: 'maintained', display: 'Maintained' },
      ],
      selectedModel: {},
      referenceList: [],
      errorMessage: '',
      GEMS: [],
      showModelTable: false,
      showLoader: false,
      tablePaginationOpts: {
        enabled: true,
        perPage: 50,
        position: 'bottom',
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
          response.data.forEach((model) => {
            $.extend(model, model.sample);
            model.sample = [model.sample.tissue, model.sample.cell_type, model.sample.cell_line] // eslint-disable-line no-param-reassign
              .filter(e => e).join(' ‒ ') || '-';
            models.push(model);
          });
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
          this.referenceList = model.ref;
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
            const { sample } = gem;
            delete gem.sample;
            const gemex = $.extend(gem, sample);
            gemex.tissue = [gemex.tissue, gemex.cell_type, gemex.cell_line].filter(e => e).join(' ‒ ') || '-';
            delete gemex.cell_type;
            gemex.stats = `reactions:&nbsp;${gem.reaction_count === null ? '-' : gem.reaction_count}<br>metabolites:&nbsp;${gemex.metabolite_count === null ? '-' : gemex.metabolite_count}<br>genes:&nbsp;${gemex.gene_count === null ? '-' : gemex.gene_count}`;
            delete gemex.reaction_count; delete gemex.gene_count; delete gemex.metabolite_count;
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
          this.columns[4].filterOptions.filterDropdownItems = Array.from(conditionDropDownFilter).sort();

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

<style lang="scss">
// style copy-pasted from https://github.com/xaksis/vue-good-table/blob/master/src/styles/_table.scss
// fixes the broken row highlight when table is striped https://github.com/xaksis/vue-good-table/pull/682
table.vgt-table tr.clickable:hover{
  background-color: #F1F5FD;
}
</style>
