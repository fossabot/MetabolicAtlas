<template>
  <div id="metabolite-page">
    <div v-if="componentNotFound" class="columns is-centered">
      <notFound component="metabolite" :component-id="mId"></notFound>
    </div>
    <div v-else>
      <div class="columns">
        <div class="column">
          <h3 class="title is-3">
            Metabolite {{ metabolite.name }}
            <span class="is-size-5 has-text-grey">{{ metabolite.compartment }}</span>
          </h3>
        </div>
      </div>
      <div class="columns is-multiline metabolite-table is-variable is-8">
        <div class="column is-10-widescreen is-9-desktop is-full-tablet">
          <table v-if="metabolite" class="table main-table is-fullwidth">
            <tr v-for="el in mainTableKey[model.database_name]" :key="el.name">
              <td v-if="el.display" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
              <td v-else-if="el.name === 'id'"
                  class="td-key has-background-primary has-text-white-bis">
                {{ model.short_name }} ID
              </td>
              <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
              <td v-if="metabolite[el.name] !== null">
                <span v-if="el.name === 'formula'" v-html="chemicalFormula(metabolite[el.name], metabolite.charge)">
                </span>
                <span v-else-if="el.modifier" v-html="el.modifier(metabolite[el.name])">
                </span>
                <span v-else-if="el.name === 'compartment'">
                  <!-- eslint-disable-next-line max-len -->
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${idfy(metabolite[el.name])}` }"
                  >{{ metabolite[el.name] }}</router-link>
                </span>
                <span v-else>
                  {{ metabolite[el.name] }}
                </span>
              </td>
              <td v-else> - </td>
            </tr>
            <tr v-if="relatedMetabolites.length !== 0">
              <td class="td-key has-background-primary has-text-white-bis">Related metabolite(s)</td>
              <td>
                <template v-for="(rm, i) in relatedMetabolites">
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                  <br v-if="i !== 0 ">
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/metabolite/${rm.id}`}">
                    {{ rm.full_name }}
                  </router-link> in {{ rm.compartment_str }}
                </template>
              </td>
            </tr>
          </table>
          <template v-if="hasExternalID">
            <h4 class="title is-4">External databases</h4>
            <table v-if="metabolite" id="ed-table" class="table is-fullwidth">
              <tr v-for="el in externalIDTableKey[model.database_name]" :key="el.name">
                <template v-if="metabolite[el.name] && metabolite[el.link]">
                  <td v-if="'display' in el"
                      class="td-key has-background-primary has-text-white-bis"
                      v-html="el.display"></td>
                  <td v-else
                      class="td-key has-background-primary has-text-white-bis">
                    {{ reformatTableKey(el.name) }}
                  </td>
                  <td>
                    <a :href="`${metabolite[el.link]}`" target="_blank">{{ metabolite[el.name] }}</a>
                  </td>
                </template>
              </tr>
            </table>
          </template>
        </div>
        <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
          <router-link class="button is-info is-fullwidth is-outlined"
                       :to="{path: `/explore/interaction/${model.database_name}/${mId}`}">
            <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
            <span>{{ messages.interPartName }}</span>
          </router-link>
        </div>
      </div>
      <div class="columns">
        <reactome v-show="showReactome" id="metabolite-reactome" :model="model" :metabolite-i-d="metaboliteID"
                  :disable-but="relatedMetabolites.length === 0">
        </reactome>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Reactome from '@/components/explorer/gemBrowser/Reactome';
import NotFound from '@/components/NotFound';
import { chemicalFormula } from '../../../helpers/chemical-formatters';
import { reformatTableKey, reformatStringToLink, addMassUnit, idfy } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'Metabolite',
  components: {
    NotFound,
    Reactome,
  },
  props: {
    model: Object,
  },
  data() {
    return {
      messages,
      mId: this.$route.params.id,
      metaboliteID: '',
      mainTableKey: {
        human1: [
          { name: 'id' },
          { name: 'name' },
          { name: 'alt_name', display: 'Alternate name' },
          { name: 'aliases', display: 'Synonyms' },
          { name: 'description' },
          { name: 'formula' },
          { name: 'charge' },
          { name: 'inchi', display: 'InChI' },
          { name: 'compartment' },
        ],
        yeast8: [
          { name: 'id' },
          { name: 'name' },
          { name: 'alt_name', display: 'Alternate name' },
          { name: 'aliases', display: 'Synonyms' },
          { name: 'description' },
          { name: 'formula' },
          { name: 'charge' },
          { name: 'inchi', display: 'InChI' },
          { name: 'compartment' },
        ],
      },
      externalIDTableKey: {
        human1: [
          { name: 'kegg_id', display: 'KEGG', link: 'kegg_link' },
          { name: 'bigg_id', display: 'BiGG', link: 'bigg_link' },
          { name: 'hmdb_id', display: 'HMDB', link: 'hmdb_link' },
          { name: 'chebi_id', display: 'ChEBI', link: 'chebi_link' },
          { name: 'pubchem_id', display: 'PubChem', link: 'pubchem_link' },
          { name: 'lipidmaps_id', display: 'Lipidmaps', link: 'lipidmaps_link' },
          { name: 'metanetx_id', display: 'MetaNetX', link: 'metanetx_link' },
        ],
        yeast8: [
        ],
      },
      metabolite: '',
      relatedMetabolites: [],
      componentNotFound: false,
      activePanel: 'table',
      showReactome: false,
    };
  },
  computed: {
    hasExternalID() {
      for (let i = 0; i < this.externalIDTableKey[this.model.database_name].length; i += 1) {
        const item = this.externalIDTableKey[this.model.database_name][i];
        if (this.metabolite[item.name] && this.metabolite[item.link]) {
          return true;
        }
      }
      return false;
    },
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/metabolite/')) {
        if (this.mId !== this.$route.params.id) {
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
      this.mId = this.$route.params.id;
      if (this.mId) {
        this.load();
      }
    },
    load() {
      axios.get(`${this.model.database_name}/metabolite/${this.mId}/`)
        .then((response) => {
          this.componentNotFound = false;
          this.metaboliteID = this.mId;
          this.metabolite = response.data;
          this.showReactome = true;
          this.getRelatedMetabolites();
        })
        .catch(() => {
          this.componentNotFound = true;
          this.showReactome = false;
          document.getElementById('search').focus();
        });
    },
    getRelatedMetabolites() {
      axios.get(`${this.model.database_name}/metabolite/${this.mId}/related`)
        .then((response) => {
          this.relatedMetabolites = response.data;
          this.relatedMetabolites.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
        })
        .catch(() => {
          this.relatedMetabolites = [];
        });
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    reformatLink(s, link) { return reformatStringToLink(s, link); },
    reformatMass(s) { return addMassUnit(s); },
    idfy,
    chemicalFormula,
  },
};
</script>

<style lang="scss">

.metabolite-table, .model-table, .reaction-table, .subsystem-table {
  .main-table tr td.td-key, #ed-table tr td.td-key {
    width: 150px;
  }
}

</style>
