<template>
  <div v-if="componentNotFound" class="columns is-centered">
    <notFound :type="type" :component-id="cName"></notFound>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-3"><span class="is-capitalized">{{ type }}</span> {{ compartment.name }}</h3>
      </div>
    </div>
    <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
    <div v-else class="columns is-multiline is-variable is-8">
      <div class="subsystem-table column is-10-widescreen is-9-desktop is-full-tablet">
        <div class="table-container">
          <table v-if="compartment && Object.keys(compartment).length != 0"
                 class="table main-table is-fullwidth">
            <tr>
              <td class="td-key has-background-primary has-text-white-bis">Name</td>
              <td> {{ compartment.name }}</td>
            </tr>
            <tr>
              <td class="td-key has-background-primary has-text-white-bis">Subsystems</td>
              <td>
                <div v-html="subsystemListHtml"></div>
                <div v-if="!showFullSubsystem && subsystems.length > limitSubsystem">
                  <br>
                  <button class="is-small button" @click="showFullSubsystem=true">
                    ... and {{ subsystems.length - limitSubsystem }} more
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td class="td-key has-background-primary has-text-white-bis">Reactions</td>
              <td> {{ compartment.reaction_count }}</td>
            </tr>
            <tr>
              <td class="td-key has-background-primary has-text-white-bis">Metabolites</td>
              <td> {{ compartment.metabolite_count }}</td>
            </tr>
            <tr>
              <td class="td-key has-background-primary has-text-white-bis">Genes</td>
              <td> {{ compartment.gene_count }}</td>
            </tr>
          </table>
        </div>
        <p>The
          <a :href="`/api/${model.database_name}/compartment/${cName}/`"
             target="_blank">complete list in JSON format</a>
          of reactions / metabolites / genes is available using our
          <a href="/api/" target="_blank">API</a></p>
      </div>
      <div class="column is-2-widescreen is-3-desktop is-half-tablet has-text-centered">
        <maps-available :id="cName" :type="type" :element-i-d="''" />
        <gem-contact :id="cName" :type="type" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import Loader from '@/components/Loader';
import NotFound from '@/components/NotFound';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import GemContact from '@/components/shared/GemContact';
import { buildCustomLink } from '@/helpers/utils';

export default {
  name: 'Subsystem',
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    GemContact,
  },
  data() {
    return {
      cName: '',
      type: 'compartment',
      errorMessage: '',
      showFullSubsystem: false,
      limitSubsystem: 30,
      componentNotFound: false,
      showLoaderMessage: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
    ...mapGetters({
      compartment: 'compartments/info',
      subsystems: 'compartments/subsystems',
    }),
    subsystemListHtml() {
      const l = ['<span class="tags">'];
      const sortedSubsystemList = this.subsystems.concat().sort((a, b) => (a.name < b.name ? -1 : 1));
      for (let i = 0; i < sortedSubsystemList.length; i += 1) {
        const s = sortedSubsystemList[i];
        if (!this.showFullSubsystem && i === this.limitSubsystem) {
          break;
        }
        const customLink = buildCustomLink({ model: this.model.database_name, type: 'subsystem', id: s.id, title: s.name });
        l.push(`<span id="${s.id}" class="tag sub">${customLink}</span>`);
      }
      l.push('</span>');
      return l.join('');
    },
  },
  watch: {
    $route() {
      this.setup();
    },
  },
  beforeMount() {
    this.setup();
  },
  methods: {
    async setup() {
      this.showLoaderMessage = 'Loading compartment data';
      this.cName = this.$route.params.id;
      try {
        const payload = { model: this.model.database_name, id: this.cName };
        await this.$store.dispatch('compartments/getCompartmentSummary', payload);
        this.componentNotFound = false;
        this.showLoaderMessage = '';
      } catch {
        this.componentNotFound = true;
        document.getElementById('search').focus();
      }
    },
  },
};
</script>

<style lang="scss">
</style>
