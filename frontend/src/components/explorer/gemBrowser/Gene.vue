<template>
  <div class="connected-metabolites">
    <div v-if="errorMessage" class="columns">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-show="!errorMessage">
      <div class="container columns">
        <div class="column">
          <h3 class="title is-3">
          Gene {{ gene.geneName }}
          </h3>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div class="columns is-multiline is-variable is-8">
            <div id="gene-details" class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
              <table v-if="gene && Object.keys(gene).length != 0" class="table main-table is-fullwidth">
                <tr v-for="el in mainTableKey[model.database_name]">
                  <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                  <td v-else-if="el.name == 'id'" class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
                  <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                  <td v-if="gene[el.name]">
                    <span v-if="'modifier' in el" v-html="el.modifier(gene)">
                    </span>
                    <span v-else>
                      {{ gene[el.name] }}
                    </span>
                  </td>
                  <td v-else> - </td>
                </tr>
              </table>
              <template v-if="hasExternalID">
                <h4 class="title is-4">External links</h4>
                <table v-if="gene && Object.keys(gene).length != 0" id="ed-table" class="table is-fullwidth">
                  <tr v-for="el in externalIDTableKey[model.database_name]" v-if="gene[el.name] && gene[el.link]">
                    <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                    <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                    <td>
                      <a :href="`${gene[el.link]}`" target="_blank">{{ gene[el.name] }}</a>
                    </td>
                  </tr>
                </table>
              </template>
            </div>
            <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
              <router-link class="button is-info is-fullwidth is-outlined"
                :to="{ path: `/explore/gem-browser/${model.database_name}/interaction/${gene.id}` }">
                <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
                <span>{{ messages.interPartName }}</span>
              </router-link>
            </div>
          </div>
          <template v-if="!this.showLoader">
            <h4 class="title is-4">Reactions</h4>
          </template>
          <div class="columns">
            <div class="column">
              <template v-if="!this.showLoader && this.showReactionLoader">
                <loader></loader>
              </template>
              <template v-else-if="!this.showReactionLoader">
                <reaction-table :reactions="this.reactions" :showSubsystem="true" :model="this.model" :limit="this.limitReaction"></reaction-table>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';
import Loader from '@/components/Loader';
import { reformatTableKey } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'gene',
  components: {
    ReactionTable,
    Loader,
  },
  props: ['model'],
  data() {
    return {
      messages,
      showLoader: true,
      showReactionLoader: true,
      errorMessage: null,
      eId: '',
      gene: {},
      geneName: '',
      mainTableKey: {
        human1: [
          { name: 'geneName', display: 'Gene&nbsp;name' },
          { name: 'description', display: 'Description' },
          { name: 'gene_synonyms', display: 'Synonyms' },
          { name: 'function' },
          { name: 'id' },
        ],
        yeast8: [
          { name: 'geneName', display: 'Gene&nbsp;name' },
          { name: 'prot_name', display: 'Protein&nbsp;name' },
          { name: 'gene_synonyms', display: 'Synonyms' },
          { name: 'function' },
          { name: 'id' },
        ],
      },
      externalIDTableKey: {
        human1: [
          { name: 'id', display: 'Ensembl', link: 'ensembl_link' },
          { name: 'hpa_id', display: 'Protein Atlas', link: 'hpa_link' },
          { name: 'uniprot_id', display: 'Uniprot', link: 'uniprot_link' },
          { name: 'ncbi_id', display: 'NCBI', link: 'ncbi_link' },
        ],
        yeast8: [],
      },
      reactions: [],
      limitReaction: 200,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/gene/')) {
        if (this.eId !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  computed: {
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model.database_name]) {
        if (this.gene[item.name] && this.gene[item.link]) {
          return true;
        }
      }
      return false;
    },
  },
  methods: {
    setup() {
      this.eId = this.$route.params.id;
      if (this.eId) {
        this.load();
        this.loadReactions();
      }
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    load() {
      this.showLoader = true;
      // const geneId = this.eid;
      axios.get(`${this.model.database_name}/gene/${this.eId}/`)
        .then((response) => {
          this.showLoader = false;
          this.errorMessage = null;
          this.eId = response.data.id;
          this.geneName = response.data.name || response.data.id;
          this.gene = response.data;
          this.gene.geneName = this.geneName;
        })
        .catch((error) => {
          this.showLoader = false;
          this.reactions = [];
          switch (error.response.status) {
            case 404:
              this.errorMessage = messages.notFoundError;
              break;
            default:
              this.errorMessage = messages.unknownError;
          }
        });
    },
    loadReactions() {
      // this.reactions = [];
      this.showReactionLoader = true;
      axios.get(`${this.model.database_name}/gene/${this.eId}/get_reactions`)
        .then((response) => {
          this.reactions = response.data;
          this.showReactionLoader = false;
        })
        .catch(() => {
          this.reactions = [];
        });
    },
  },
  beforeMount() {
    this.setup();
  },
};

</script>

<style lang="scss">
</style>
