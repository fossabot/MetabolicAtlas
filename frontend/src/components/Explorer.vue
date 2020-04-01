<template>
  <section :class="{ 'section extended-section' : !extendWindow }">
    <div :class="{ 'container': !extendWindow }">
      <template v-if="modelNotFound">
        <div class="columns is-centered">
          <notFound type="model" :component-id="modelNotFound"></notFound>
        </div>
      </template>
      <template v-else-if="currentShowComponent">
        <keep-alive>
          <component :is="currentShowComponent"></component>
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
        <div v-if="model" class="columns is-centered">
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
          <div class="column has-text-centered">
            <p class="has-text-weight-bold is-size-5">2. Select a tool:</p>
          </div>
        </div>
        <div v-if="model" class="columns is-multiline is-centered">
          <template v-for="tool in explorerTools">
            <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
            <div class="column is-3-widescreen is-4-desktop is-6-tablet is-full-mobile is-size-5">
              <router-link :to="{ name: tool.routeName, params: { model: model.database_name } }"
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
import { mapGetters, mapState } from 'vuex';
import GemBrowser from '@/components/explorer/GemBrowser';
import MapViewer from '@/components/explorer/MapViewer';
import InteractionPartners from '@/components/explorer/InteractionPartners';
import NotFound from '@/components/NotFound';
import { default as EventBus } from '../event-bus';
import { default as messages } from '../helpers/messages';

export default {
  name: 'Explorer',
  components: {
    GemBrowser,
    MapViewer,
    InteractionPartners,
    NotFound,
  },
  data() {
    return {
      /* eslint-disable global-require */
      explorerTools: [
        { name: messages.gemBrowserName,
          img: require('../assets/gemBrowser.jpg'),
          routeName: 'browserRoot',
          icon: 'table' },
        { name: messages.mapViewerName,
          img: require('../assets/mapViewer.jpg'),
          routeName: 'viewerRoot',
          icon: 'map-o' },
        { name: messages.interPartName,
          img: require('../assets/interaction.jpg'),
          routeName: 'interPartnerRoot',
          icon: 'share-alt' },
      ],
      modelNotFound: null,
      extendWindow: false,
      currentShowComponent: '',

      compartments: {},
      errorMessage: '',
    };
  },
  computed: {
    ...mapGetters({
      models: 'models/models',
    }),
    ...mapState({
      model: state => state.models.model,
    }),
  },
  watch: {
    /* eslint-disable-next-line quote-props */
    '$route': function watchSetup() {
      this.setup();
      this.updateRoute();
    },
  },
  async created() {
    this.setup();
    await this.getModelList();

    EventBus.$on('showMapViewer', () => {
      this.displayViewer();
    });
    EventBus.$on('showGemBrowser', () => {
      this.displayBrowser();
    });
    EventBus.$on('showInteractionPartner', () => {
      this.displayInterPartner();
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
      if (['viewerRoot', 'viewer'].includes(this.$route.name)) {
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
    async getModelList() {
      // get integrated models list
      try {
        await this.$store.dispatch('models/getModels');

        const defaultModelKey = Object.keys(this.models).sort(
          (a, b) => (a.toLowerCase() < b.toLowerCase() ? -1 : 1))[0];
        console.log(defaultModelKey);
        let defaultModel = this.models[defaultModelKey];
        if (this.$route.params.model && this.$route.params.model in this.models) {
          // if a model DB is provide in the URL, use it to select the model
          defaultModel = this.models[this.$route.params.model];
        } else if (this.$route.name === 'explorerRoot' && this.$route.query && this.$route.query.selected) {
          // or if a selected=NAME is provided in the URL, try to use it to select the model
          const modelShortNamesDict = {};
          Object.values(this.models).forEach((m) => { modelShortNamesDict[m.short_name] = m; });
          if (this.$route.query.selected in modelShortNamesDict) {
            defaultModel = modelShortNamesDict[this.$route.query.selected];
          }
        }
        this.$store.dispatch('models/selectModel', defaultModel);
        this.setup();
      } catch {
        this.errorMessage = messages.unknownError;
      }
    },
    selectModel(model) {
      if (!this.model || model.database_name !== this.model.database_name) {
        this.$store.dispatch('models/selectModel', model);
      }
      this.updateRoute(this.model.short_name);
    },
    updateRoute(modelName) {
      if (this.$route.name === 'explorerRoot' && this.model && (!this.$route.query || !this.$route.query.selected || this.$route.query.selected !== modelName)) {
        this.$router.replace({ name: 'explorerRoot', query: { selected: this.model.short_name } }).catch(() => {});
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
