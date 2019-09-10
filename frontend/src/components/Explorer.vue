<template>
  <section :class="{ 'section extended-section' : !extendWindow }">
    <div :class="{ 'container': !extendWindow }">
      <template v-if="currentShowComponent">
        <keep-alive>
          <component v-bind:is="currentShowComponent" :model="model"></component>
        </keep-alive>
      </template>
      <template v-else>
        <div class="columns has-text-centered">
          <div class="column">
            <h4 class="is-size-3 has-text-weight-bold">Explore the integrated models</h4>
          </div>
        </div>
        <div class="columns">
          <div class="column has-text-centered-tablet">
            <p class="has-text-weight-bold is-size-5">
              Select a model:
            </p>
          </div>
        </div>
        <div class="columns is-centered">
          <div class="column is-8-widescreen is-10-desktop is-fullwidth-tablet is-size-5">
            <div id="selectedModel"
            :class="cmodel.database_name === model.database_name ? 'selectedBox' : ''" class="box has-text-centered clickable"
            v-for="cmodel, k in Object.values(models).sort((a, b) => (a.short_name.toLowerCase() < b.short_name.toLowerCase() ? -1 : 1))"
            @mousedown.prevent="selectModel(cmodel)"
            :title="`Select ${cmodel.short_name} as the model to explore`">
              <div>
                <span class="has-text-primary has-text-weight-bold">{{cmodel.short_name}} v{{cmodel.version}}</span> - {{cmodel.full_name}}
              </div>
              <div class="has-text-grey">
                {{cmodel.reaction_count}} reactions -
                {{cmodel.metabolite_count}} metabolites -
                {{cmodel.gene_count}} genes
              </div>
            </div>
          </div>
        </div>
        <br>
        <div class="columns">
          <div class="column has-text-centered-tablet">
            <p class="has-text-weight-bold is-size-5">
              Select a tool:
            </p>
          </div>
        </div>
        <div class="columns is-centered">
          <template v-for="tool in explorerTools">
            <div class="column is-4-widescreen is-5-desktop">
              <router-link :to="{ path: `${tool.url}/${model.database_name }` }" :title="`Click to access the ${tool.name} for ${model.short_name} model`">
                <div class="card card-fullheight card-selectable has-text-justified">
                  <header class="card-header">
                    <p class="card-header-title is-size-5">{{ tool.name }}</p>
                  </header>
                  <div class="card-content">
                    <div class="content">
                        <img :src="tool.img" />
                    </div>
                  </div>
                </div>
            </router-link>
            </div>
          </template>
        </div>
      </template>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import GemBrowser from '@/components/explorer/GemBrowser';
import MapViewer from '@/components/explorer/MapViewer';
import { idfy } from '../helpers/utils';
import { default as EventBus } from '../event-bus';
import { default as messages } from '../helpers/messages';

export default {
  name: 'explorer',
  components: {
    GemBrowser,
    MapViewer,
  },
  data() {
    return {
      /* eslint-disable global-require*/
      explorerTools: [
        { name: messages.gemBrowserName,
          img: require('../assets/gemBrowser.jpg'),
          url: '/explore/gem-browser',
        },
        { name: messages.mapViewerName,
          img: require('../assets/mapViewer.jpg'),
          url: '/explore/map-viewer',
        },
      ],
      model: null,
      models: {},
      extendWindow: false,
      currentShowComponent: '',

      compartments: {},
      errorMessage: '',
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.setup();
    next();
  },
  created() {
    this.setup();
    this.getModelList();

    EventBus.$on('requestViewer', (type, name, ids, forceReload) => {
      this.displayViewer();
      EventBus.$emit('showAction', type, name, ids, forceReload);
    });
    EventBus.$on('showMapViewer', () => {
      this.displayViewer();
    });
    EventBus.$on('showGemBrowser', () => {
      this.displayBrowser();
    });

    $('body').on('click', 'td m', function f() {
      if (!($(this).hasClass('cms'))) {
        EventBus.$emit('GBnavigateTo', 'metabolite', $(this).attr('class'));
      }
    });
    $('body').on('click', 'span.rcm', function f() {
      EventBus.$emit('GBnavigateTo', 'metabolite', $(this).attr('id'));
    });
    $('body').on('click', 'span.rce', function f() {
      EventBus.$emit('GBnavigateTo', 'gene', $(this).attr('id'));
    });

    $('body').on('click', 'span.sub', function f() {
      EventBus.$emit('GBnavigateTo', 'subsystem', $(this).attr('id'));
    });
    $('body').on('click', 'a.cmp', function f() {
      EventBus.$emit('GBnavigateTo', 'compartment', idfy($(this).html()));
    });
  },
  methods: {
    setup() {
      if (!this.model) {
        // do not redirect on url change unless the model is already loaded
        return;
      }
      // but redirect even if the model url do not match the model loaded
      if (this.$route.params.model && this.$route.params.model in this.models) {
        this.selectModel(this.models[this.$route.params.model]);
      }
      if (['viewer', 'viewerCompartment', 'viewerCompartmentRea', 'viewerSubsystem', 'viewerSubsystemRea'].includes(this.$route.name)) {
        this.displayViewer();
      } else if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        this.displayBrowser();
      } else {
        EventBus.$emit('destroy3Dnetwork');
        this.extendWindow = false;
        this.currentShowComponent = '';
      }
    },
    getModelList() {
      // get integrated models list
      axios.get('models/')
        .then((response) => {
          const models = {};
          for (const model of response.data) {
            models[model.database_name] = model;
          }
          this.models = models;
          let defaultModel = this.models.human1;
          if (this.$route.params.model && this.$route.params.model in this.models) {
            defaultModel = this.models[this.$route.params.model];
          }
          this.selectModel(defaultModel);
          this.setup();
        })
        .catch(() => {
          this.errorMessage = messages.unknownError;
        });
    },
    selectModel(model) {
      if (!this.model || model.database_name !== this.model.database_name) {
        this.model = model;
        EventBus.$emit('modelSelected', this.model);
      }
    },
    displayBrowser() {
      this.extendWindow = false;
      this.currentShowComponent = 'GemBrowser';
    },
    displayViewer() {
      this.extendWindow = true;
      this.currentShowComponent = 'MapViewer';
    },
  },
};

</script>

<style lang="scss">

#selectedModel.selectedBox {
  box-shadow: 0 2px 3px $primary, 0 0 0 1px $primary;
}

</style>
