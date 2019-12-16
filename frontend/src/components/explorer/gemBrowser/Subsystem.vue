<template>
  <div v-if="componentNotFound" class="columns is-centered">
    <notFound component="subsystem" :componentID="sName"></notFound>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-3">Subsystem {{ !showLoader ? info.name : '' }}</h3>
      </div>
    </div>
    <loader v-show="showLoader"></loader>
    <div v-show="!showLoader" class="columns is-multiline is-variable is-8">
      <div class="subsystem-table column is-10-widescreen is-9-desktop is-full-tablet">
        <table v-if="info && Object.keys(info).length != 0" class="table main-table is-fullwidth">
          <tr v-for="el in mainTableKey[model.database_name]"
              :key="el.name_id"
              class="m-row">
            <template v-if="info[el.name]">
              <td v-if="el.display" class="td-key has-background-primary has-text-white-bis">{{ el.display }}</td>
              <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatKey(el.name) }}</td>
              <td v-if="info[el.name]">
                <span v-if="el.modifier" v-html="el.modifier(info[el.name])">
                </span>
                <span v-else>
                  {{ info[el.name] }}
                </span>
              </td>
              <td v-else> - </td>
            </template>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Compartments</td>
            <td>
              <template v-for="(c, i) in info['compartment']">
                <template v-if="i !== 0">, </template>
                <!-- eslint-disable-next-line vue/valid-v-for -->
                <router-link
                  :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${idfy(c)}` }"
                > {{ c }}</router-link>
              </template>
            </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Metabolites</td>
            <td>
              <div v-html="metabolitesListHtml"></div>
              <div v-if="!showFullMetabolite && metabolites.length > displayedMetabolite">
                <br>
                <button class="is-small button" @click="showFullMetabolite=true">
                  ... and {{ metabolites.length - displayedMetabolite }} more
                </button>
                <span v-show="metabolites.length == limitMetabolite" class="tag is-medium is-warning is-pulled-right">
                  The number of metabolites displayed is limited to {{ limitMetabolite }}.
                </span>
              </div>
            </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Genes</td>
            <td>
              <div v-html="genesListHtml"></div>
              <div v-if="!showFullGene && genes.length > displayedGene">
                <br>
                <button class="is-small button" @click="showFullGene=true">
                  ... and {{ genes.length - displayedGene }} more
                </button>
                <span v-show="genes.length == limitGene" class="tag is-medium is-warning is-pulled-right">
                  The number of genes displayed is limited to {{ limitGene }}.
                </span>
              </div>
            </td>
          </tr>
        </table>
      </div>
      <div class="column is-2-widescreen is-3-desktop is-half-tablet has-text-centered">
        <maps-available :id="sName" :model="model" :type="'subsystem'" :element-i-d="''"></maps-available>
      </div>
    </div>
    <template v-if="!showLoader">
      <h4 class="title is-4">Reactions</h4>
    </template>
    <div class="columns">
      <div class="column">
        <template v-if="!showLoader && showReactionLoader">
          <loader></loader>
        </template>
        <template v-else-if="!showReactionLoader">
          <reaction-table :source-name="sName" :reactions="reactions" :show-subsystem="false"
                          :model="model" :limit="1000">
          </reaction-table>
        </template>
      </div>
    </div>
  </div>
</template>


<script>

import axios from 'axios';
import Loader from '@/components/Loader';
import NotFound from '@/components/NotFound';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';
import { reformatTableKey, idfy } from '../../../helpers/utils';

export default {
  name: 'Subsystem',
  components: {
    NotFound,
    MapsAvailable,
    ReactionTable,
    Loader,
  },
  props: {
    model: {
      type: Object,
    },
  },
  data() {
    return {
      sName: this.$route.params.id,
      showLoader: true,
      showReactionLoader: true,
      info: {},
      metabolites: [],
      genes: [],
      reactions: [],
      errorMessage: '',
      mainTableKey: {
        human1: [
          { name: 'name', display: 'Name' },
        ],
      },
      showFullMetabolite: false,
      showFullGene: false,
      displayedMetabolite: 40,
      displayedGene: 40,
      limitMetabolite: 0,
      limitGene: 0,
      limitReaction: 0,
      componentNotFound: false,
      idfy,
    };
  },
  computed: {
    metabolitesListHtml() {
      const l = ['<span class="tags">'];
      const metsSorted = this.metabolites.concat().sort((a, b) => (a.name < b.name ? -1 : 1));
      for (let i = 0; i < metsSorted.length; i += 1) {
        const m = metsSorted[i];
        if ((!this.showFullMetabolite && i === this.displayedMetabolite)
          || i === this.limitMetabolite) {
          break;
        }
        l.push(
          `<span id="${m.id}" class="tag rcm"><a class="is-size-6">${m.full_name ? m.full_name : m.id}</a></span>`
        );
      }
      l.push('</span>');
      return l.join('');
    },
    genesListHtml() {
      const l = ['<span class="tags">'];
      const genesSorted = this.genes.concat().sort((a, b) => (a.name < b.name ? -1 : 1));
      for (let i = 0; i < genesSorted.length; i += 1) {
        const e = genesSorted[i];
        if ((!this.showFullGene && i === this.displayedGene)
          || i === this.limitGene) {
          break;
        }
        l.push(`<span id="${e.id}" class="tag rce"><a class="is-size-6">${e.name ? e.name : e.id}</a></span>`);
      }
      l.push('</span>');
      return l.join('');
    },
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/gem-browser/') && this.$route.path.includes('/subsystem/')) {
        if (this.sName !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  beforeMount() {
    this.setup();
  },
  methods: {
    setup() {
      this.sName = this.$route.params.id;
      this.load();
      this.getReactions();
    },
    load() {
      this.showLoader = true;
      axios.get(`${this.model.database_name}/subsystem/${this.sName}/summary/`)
        .then((response) => {
          this.componentNotFound = false;
          this.info = response.data.info;
          this.metabolites = response.data.metabolites;
          this.genes = response.data.genes;
          this.limitMetabolite = response.data.limit;
          this.limitGene = response.data.limit;
          this.showLoader = false;
        })
        .catch(() => {
          this.componentNotFound = true;
          document.getElementById('search').focus();
        });
    },
    getReactions() {
      this.showReactionLoader = true;
      axios.get(`${this.model.database_name}/subsystem/${this.sName}/get_reactions`)
        .then((response) => {
          this.reactions = response.data.reactions;
          this.limitReaction = response.data.limit;
          this.showReactionLoader = false;
        })
        .catch(() => {
        });
    },
    reformatKey(k) { return reformatTableKey(k); },
  },
};
</script>

<style lang="scss">
</style>
