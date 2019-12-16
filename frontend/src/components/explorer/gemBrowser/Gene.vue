<template>
  <div class="connected-metabolites">
    <div v-if="componentNotFound" class="columns is-centered">
      <notFound component="gene" :componentID="eId"></notFound>
    </div>
    <div v-else>
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
                <tr v-for="el in mainTableKey[model.database_name]" :key="el.name">
                  <td v-if="'display' in el"
                      class="td-key has-background-primary has-text-white-bis"
                      v-html="el.display"></td>
                  <td v-else-if="el.name == 'id'"
                      class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
                  <td v-else
                      class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
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
                <h4 class="title is-4">External databases</h4>
                <table v-if="gene && Object.keys(gene).length != 0" id="ed-table" class="table is-fullwidth">
                  <tr v-for="el in externalIDTableKey[model.database_name]" :key="el.name">
                    <template v-if="gene[el.name] && gene[el.link]">
                      <td v-if="'display' in el"
                          class="td-key has-background-primary has-text-white-bis"
                          v-html="el.display"></td>
                      <td v-else
                          class="td-key has-background-primary has-text-white-bis">
                        {{ reformatTableKey(el.name) }}
                      </td>
                      <td>
                        <a :href="`${gene[el.link]}`" target="_blank">{{ gene[el.name] }}</a>
                      </td>
                    </template>
                  </tr>
                </table>
              </template>
            </div>
            <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
              <router-link class="button is-info is-fullwidth is-outlined"
                           :to="{ path: `/explore/interaction/${model.database_name}/${gene.id}` }">
                <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
                <span>{{ messages.interPartName }}</span>
              </router-link>
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
                <reaction-table :source-name="geneName" :reactions="reactions" :show-subsystem="true"
                                :model="model" :limit="limitReaction">
                </reaction-table>
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
import NotFound from '@/components/NotFound';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';
import Loader from '@/components/Loader';
import { reformatTableKey } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'Gene',
  components: {
    NotFound,
    ReactionTable,
    Loader,
  },
  props: {
    model: Object,
  },
  data() {
    return {
      messages,
      showLoader: true,
      showReactionLoader: true,
      eId: '',
      gene: {},
      geneName: '',
      mainTableKey: {
        human1: [
          { name: 'id' },
          { name: 'geneName', display: 'Gene&nbsp;name' },
          { name: 'description', display: 'Description' },
          { name: 'gene_synonyms', display: 'Synonyms' },
          { name: 'function' },
        ],
        yeast8: [
          { name: 'id' },
          { name: 'geneName', display: 'Gene&nbsp;name' },
          { name: 'prot_name', display: 'Protein&nbsp;name' },
          { name: 'gene_synonyms', display: 'Synonyms' },
          { name: 'function' },
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
      componentNotFound: false,
    };
  },
  computed: {
    hasExternalID() {
      for (let i = 0; i < this.externalIDTableKey[this.model.database_name].length; i += 1) {
        const item = this.externalIDTableKey[this.model.database_name][i];
        if (this.gene[item.name] && this.gene[item.link]) {
          return true;
        }
      }
      return false;
    },
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
  beforeMount() {
    this.setup();
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
          this.componentNotFound = false;
          this.eId = response.data.id;
          this.geneName = response.data.name || response.data.id;
          this.gene = response.data;
          this.gene.geneName = this.geneName;
        })
        .catch(() => {
          this.showLoader = false;
          this.reactions = [];
          this.componentNotFound = true;
          document.getElementById('search').focus();
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
};

</script>

<style lang="scss">
</style>
