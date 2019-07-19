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
          Enzyme {{ enzyme.enzymeName }}
          </h3>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div class="columns is-multiline is-variable is-8">
            <div id="enzyme-details" class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
              <table v-if="enzyme && Object.keys(enzyme).length != 0" class="table main-table is-fullwidth">
                <tr v-for="el in mainTableKey[model.database_name]">
                  <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                  <td v-else-if="el.name == 'id'" class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
                  <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                  <td v-if="enzyme[el.name]">
                    <span v-if="'modifier' in el" v-html="el.modifier(enzyme)">
                    </span>
                    <span v-else>
                      {{ enzyme[el.name] }}
                    </span>
                  </td>
                  <td v-else> - </td>
                </tr>
              </table>
              <template v-if="hasExternalID">
                <h4 class="title is-4">External links</h4>
                <table v-if="enzyme && Object.keys(enzyme).length != 0" id="ed-table" class="table is-fullwidth">
                  <tr v-for="el in externalIDTableKey[model.database_name]" v-if="enzyme[el.name] && enzyme[el.link]">
                    <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                    <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                    <td>
                      <a :href="`${enzyme[el.link]}`" target="_blank">{{ enzyme[el.name] }}</a>
                    </td>
                  </tr>
                </table>
              </template>
            </div>
            <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
              <router-link class="button is-info is-fullwidth is-outlined"
                :to="{ path: `/explore/gem-browser/${model.database_name}/interaction/${enzyme.id}` }">
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
  name: 'enzyme',
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
      enzyme: {},
      enzymeName: '',
      mainTableKey: {
        human1: [
          { name: 'enzymeName', display: 'Gene&nbsp;name' },
          { name: 'description', display: 'Description' },
          { name: 'gene_synonyms', display: 'Synonyms' },
          { name: 'function' },
          { name: 'id' },
        ],
        yeast8: [
          { name: 'enzymeName', display: 'Gene&nbsp;name' },
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
      if (this.$route.path.includes('/enzyme/')) {
        if (this.eId !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  computed: {
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model.database_name]) {
        if (this.enzyme[item.name] && this.enzyme[item.link]) {
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
      // const enzymeId = this.eid;
      axios.get(`${this.model.database_name}/enzyme/${this.eId}/`)
        .then((response) => {
          this.showLoader = false;
          this.errorMessage = null;
          this.eId = response.data.id;
          this.enzymeName = response.data.gene_name || response.data.id;
          this.enzyme = response.data;
          this.enzyme.enzymeName = this.enzymeName;
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
      axios.get(`${this.model.database_name}/enzyme/${this.eId}/get_reactions`)
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
