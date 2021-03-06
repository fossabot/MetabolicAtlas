<template>
  <section class="section section-no-top extended-section">
    <div class="container is-fullhd">
      <div v-if="errorMessage">
        {{ errorMessage }}
      </div>
      <div v-else>
        <h3 class="title is-3">Integrated GEMs</h3>
        <p class="has-text-justified">
          These models are integrated into the Metabolic Atlas database;
          they can be explored via {{ messages.gemBrowserName }}, {{ messages.mapViewerName }} and
          {{ messages.interPartName }}.
        </p><br><br>
        <div id="integrated" class="columns is-multiline is-variable is-6">
          <div v-for="model in integratedModels" :key="model.short_name"
               class="column is-4-widescreen is-5-desktop is-6-tablet">
            <div class="card">
              <header class="card-header clickable has-background-primary-lighter"
                      @click="showIntegratedModelData(model)">
                <p class="card-header-title card-content has-text-primary">
                  {{ model.short_name }} {{ model.version }}
                </p>
                <div class="card-header-icon">
                  <span class="icon has-text-primary">
                    <i class="fa fa-plus-square"></i>
                  </span>
                </div>
              </header>
              <div class="card-content card-fullheight">
                <p class="has-text-justified">{{ model.full_name }}</p><br>
                <p>
                  Reactions: {{ model.reaction_count }}<br>
                  Metabolites: {{ model.metabolite_count }}<br>
                  Genes: {{ model.gene_count }}<br><br>
                  Updated {{ model.date || "n/a" }} from
                  <a :href="model.link" target="_blank">
                    GitHub<span class="icon"><i class="fa fa-github"></i></span>
                  </a>
                </p>
              </div>
              <footer class="card-footer">
                <router-link class="card-footer-item is-info is-outlined"
                             :to="{ name: 'browserRoot', params: { model: model.database_name } }">
                  <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
                  <span>{{ messages.gemBrowserName }}</span>
                </router-link>
                <router-link class="card-footer-item is-info is-outlined"
                             :to="{ name: 'viewerRoot', params: { model: model.database_name } }">
                  <span class="icon is-large"><i class="fa fa-map-o fa-lg"></i></span>
                  <span>{{ messages.mapViewerName }}</span>
                </router-link>
              </footer>
            </div>
          </div>
        </div>
        <br>
        <h3 class="title is-3">GEM Repository</h3>
        <p class="has-text-justified">
          While we do not provide support for these models, we are making them available to download.
          For support, the authors should be contacted. They are listed in the <i>References</i> section of each model.
          Click on a row to display more information. To download multiple models at once use the
          <router-link :to=" { name: 'documentation', hash: '#FTP-download'} ">FTP server</router-link>.
        </p>
        <br>
        <loader v-show="showLoader"></loader>
        <div v-if="gems.length != 0">
          <vue-good-table :columns="columns" :rows="gems" :search-options="{ enabled: true, skipDiacritics: true }"
                          :sort-options="{ enabled: true }" style-class="vgt-table striped"
                          :pagination-options="tablePaginationOpts" @on-row-click="t => getModelData(t.row.id)">
          </vue-good-table>
        </div>
        <div v-else>
          <span v-if="!showLoader">No models available</span>
        </div>
        <br>
        <div v-if="showModelId" id="gem-list-modal" class="modal is-active">
          <div class="modal-background" @click="showModelId = ''"></div>
          <div class="modal-content column is-6-fullhd is-8-desktop is-10-tablet is-full-mobile has-background-white"
               tabindex="0" @keyup.esc="showModelId = ''">
            <div id="modal-info" class="model-table">
              <h4 class="title is-size-4">
                <template v-if="selectedModel.database_name">
                  {{ selectedModel.full_name }}
                </template>
                <template v-else>
                  <span class="is-capitalized">{{ selectedModel.set_name }}</span> -
                  {{ selectedModel.tag || selectedModel.tissue
                    || selectedModel.cell_type || selectedModel.cell_line || "" }}
                </template>
              </h4>
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
              <br>
              <template v-if="selectedModel.files">
                <h4 class="subtitle is-size-4">Files</h4>
                <template v-for="file in selectedModel.files">
                  <a :key="file.path" class="button" :href="`${filesURL}${file.path}`">{{ file.format }}</a>&nbsp;
                </template>
                <br><br>
              </template>
            </div>
          </div>
          <button class="modal-close is-large" @click="showModelId = ''"></button>
        </div>
      </div>
    </div>
  </section>
</template>


<script>
import { mapGetters, mapState } from 'vuex';
import { VueGoodTable } from 'vue-good-table';
import 'vue-good-table/dist/vue-good-table.css';
import Loader from '@/components/Loader';
import References from '@/components/shared/References';
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
      showModelId: '',
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
      filesURL: 'https://ftp.metabolicatlas.org/',
    };
  },
  computed: {
    ...mapState({
      gems: state => state.gems.gemList,
      gem: state => state.gems.gem,
    }),
    ...mapGetters({
      integratedModels: 'models/integratedModels',
      setFilterOptions: 'gems/setFilterOptions',
      systemFilterOptions: 'gems/systemFilterOptions',
      conditionFilterOptions: 'gems/conditionFilterOptions',
    }),
  },
  watch: {
    showModelId(modelId) {
      if (modelId) {
        this.$router.push({ name: 'gemsModal', params: { model_id: modelId } });
        return;
      }
      this.$router.push({ name: 'gems' });
    },
  },
  async beforeMount() {
    await this.getIntegratedModels();
    await this.getModels();
  },
  methods: {
    async getIntegratedModels() {
      try {
        await this.$store.dispatch('models/getModels');

        if (this.$route.name === 'gemsModal') {
          const urlId = this.$route.params.model_id;
          const urlIntegrateModel = this.integratedModels.find(m => m.short_name === urlId);
          if (urlIntegrateModel) {
            this.showIntegratedModelData(urlIntegrateModel);
          } else {
            // concurrence getModels api query
            await this.getModelData(urlId);
          }
        }
      } catch {
        this.errorMessage = messages.unknownError;
      }
    },
    async getModelData(id) {
      try {
        await this.$store.dispatch('gems/getGemData', id);
        this.selectedModel = this.gem;
        this.referenceList = this.selectedModel.ref;
        this.showModelId = id;
      } catch {
        this.showModelId = '';
      }
    },
    showIntegratedModelData(model) {
      this.selectedModel = model;
      this.showModelId = model.short_name;
      this.referenceList = model.ref;
    },
    async getModels() {
      this.showLoader = true;

      try {
        await this.$store.dispatch('gems/getGems');
        this.columns[0].filterOptions.filterDropdownItems = this.setFilterOptions;
        this.columns[3].filterOptions.filterDropdownItems = this.systemFilterOptions;
        this.columns[4].filterOptions.filterDropdownItems = this.conditionFilterOptions;
        this.errorMessage = '';
        this.showLoader = false;
      } catch {
        this.errorMessage = messages.notFoundError;
        this.showLoader = false;
      }
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
