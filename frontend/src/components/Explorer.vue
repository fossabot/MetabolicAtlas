<template>
  <section :class="{ 'section extended-section' : !extendWindow }">
    <div :class="{ 'container': !extendWindow }">
      <template v-if="modelNotFound">
        <div class="columns is-centered">
          <notFoundComponent component="model" :componentID="modelNotFound"></notFoundComponent>
        </div>
      </template>
      <template v-else-if="currentShowComponent">
        <keep-alive>
          <component :is="currentShowComponent" :model="model"></component>
        </keep-alive>
      </template>
      <template v-else>
        <div class="columns has-text-centered">
          <div class="column">
            <h3 class="title is-size-3">Explore the integrated models</h3>
          </div>
        </div>
        <div class="columns">
          <div class="column has-text-centered-tablet">
            <p class="has-text-weight-bold is-size-5">1. Select a model:</p>
          </div>
        </div>
        <div class="columns is-centered">
          <div class="column is-8-widescreen is-10-desktop is-fullwidth-tablet is-size-5">
            <div v-for="cmodel in Object.values(models).sort((a, b) =>
                   (a.short_name.toLowerCase() < b.short_name.toLowerCase() ? -1 : 1))"
                 id="selectedModel" :key="cmodel.database_name"
                 class="box has-text-centered clickable hoverable"
                 :class="cmodel.database_name === model.database_name ? 'selectedBox' : ''"
                 :title="`Select ${cmodel.short_name} as the model to explore`"
                 @mousedown.prevent="selectModel(cmodel)">
              <div>
                <span :class="cmodel.database_name === model.database_name ?
                  'has-text-primary has-text-weight-bold' : ''">
                  <span v-if="cmodel.database_name === model.database_name"
                        class="icon"><i class="fa fa-check-square-o"></i></span>
                  <span v-else><i class="fa fa-square-o"></i></span>
                  {{ cmodel.short_name }} v{{ cmodel.version }}
                </span> - {{ cmodel.full_name }}
              </div>
              <div class="has-text-grey">
                {{ cmodel.reaction_count }} reactions -
                {{ cmodel.metabolite_count }} metabolites -
                {{ cmodel.gene_count }} genes
              </div>
            </div>
          </div>
        </div>
        <br>
        <div class="columns">
          <div class="column has-text-centered-tablet">
            <p class="has-text-weight-bold is-size-5">2. Select a tool:</p>
          </div>
        </div>
        <div v-if="model" class="columns is-multiline">
          <template v-for="tool in explorerTools">
            <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
            <div class="column is-one-third-widescreen is-half-desktop is-half-tablet is-fullwidth-mobile is-size-5">
              <router-link :to="{ path: `${tool.url}/${model.database_name }` }"
                           :title="`Click to access the ${tool.name} for ${model.short_name} model`">
                <div class="card card-fullheight hoverable">
                  <header class="card-header">
                    <p class="card-header-title is-centered">
                      <span class="icon is-medium"><i :class="`fa fa-${tool.icon}`"></i></span>
                      &nbsp;{{ tool.name }}&nbsp;&nbsp;
                      <span class="has-text-grey-light">{{ model.short_name }}</span>
                    </p>
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
  </section>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import GemBrowser from '@/components/explorer/GemBrowser';
import MapViewer from '@/components/explorer/MapViewer';
import InteractionPartners from '@/components/explorer/InteractionPartners';
import NotFoundComponent from '@/components/explorer/gemBrowser/NotFoundComponent';
import { idfy } from '../helpers/utils';
import { default as EventBus } from '../event-bus';
import { default as messages } from '../helpers/messages';

export default {
  name: 'Explorer',
  components: {
    GemBrowser,
    MapViewer,
    InteractionPartners,
    NotFoundComponent,
  },
  data() {
    return {
      /* eslint-disable global-require */
      explorerTools: [
        { name: messages.gemBrowserName,
          img: require('../assets/gemBrowser.jpg'),
          url: '/explore/gem-browser',
          icon: 'table' },
        { name: messages.mapViewerName,
          img: require('../assets/mapViewer.jpg'),
          url: '/explore/map-viewer',
          icon: 'map-o' },
        { name: messages.interPartName,
          img: require('../assets/interaction.png'),
          url: '/explore/interaction',
          icon: 'share-alt' },
      ],
      model: null,
      models: {},
      modelNotFound: null,
      extendWindow: false,
      currentShowComponent: '',

      compartments: {},
      errorMessage: '',
    };
  },
  watch: {
    /* eslint-disable-next-line quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  beforeRouteUpdate(to, from, next) { // eslint-disable-line no-unused-vars
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
    EventBus.$on('showInteractionPartner', () => {
      this.displayInterPartner();
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
      if (this.$route.params.model) {
        if (this.$route.params.model in this.models) {
          this.selectModel(this.models[this.$route.params.model]);
        } else {
          this.modelNotFound = this.$route.params.model;
          return;
        }
      }
      this.modelNotFound = null;
      if (['viewer', 'viewerCompartment', 'viewerCompartmentRea', 'viewerSubsystem', 'viewerSubsystemRea'].includes(this.$route.name)) {
        this.displayViewer();
      } else if (['browserRoot', 'browser'].includes(this.$route.name)) {
        this.displayBrowser();
      } else if (['interPartnerRoot', 'interPartner'].includes(this.$route.name)) {
        this.displayInterPartner();
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
          response.data.forEach((model) => {
            models[model.database_name] = model;
          });
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
    displayInterPartner() {
      this.extendWindow = false;
      this.currentShowComponent = 'InteractionPartners';
    },
  },
};

</script>

<style lang="scss">

#selectedModel.selectedBox {
  box-shadow: $shadow-primary-light;
}

</style>
