<template>
  <div id="metabolite-page">
    <div v-if="errorMessage" class="columns">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-else>
      <div class="columns">
        <div class="column">
          <h3 class="title is-3">Metabolite {{ metabolite.name }}</h3>
        </div>
      </div>
      <div class="columns is-multiline metabolite-table is-variable is-8">
        <div class="column is-10-widescreen is-9-desktop is-full-tablet">
          <table v-if="metabolite && Object.keys(metabolite).length !== 0" class="table main-table is-fullwidth">
            <tr v-for="el in mainTableKey[model.database_name]">
              <td v-if="el.display" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
              <td v-else-if="el.name === 'id'" class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
              <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
              <td v-if="metabolite[el.name] !== null">
                <span v-if="el.name === 'formula'" v-html="chemicalFormula(metabolite[el.name], metabolite.charge)">
                </span>
                <span v-else-if="el.modifier" v-html="el.modifier(metabolite[el.name])">
                </span>
                <span v-else-if="el.name === 'compartment'">
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${idfy(metabolite[el.name])}` }">{{ metabolite[el.name] }}</router-link>
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
                  <br v-if="i !== 0 ">
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/metabolite/${rm.id}`}">
                    {{ rm.name }}
                  </router-link> ({{ rm.compartment_str }})
                </template>
              </td>
            </tr>
          </table>
          <template v-if="hasExternalID">
            <h4 class="title is-4">External links</h4>
            <table v-if="metabolite && Object.keys(metabolite).length !== 0" id="ed-table" class="table is-fullwidth">
              <tr v-for="el in externalIDTableKey[model.database_name]" v-if="metabolite[el.name] && metabolite[el.link]">
                <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                <td>
                  <a :href="`${metabolite[el.link]}`" target="_blank">{{ metabolite[el.name] }}</a>
                </td>
              </tr>
            </table>
          </template>
        </div>
        <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
          <router-link class="button is-info is-fullwidth is-outlined"
            :to="{path: `/explore/gem-browser/${model.database_name}/interaction/${this.mId}`}">
            <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
            <span>{{ messages.interPartName }}</span>
          </router-link>
        </div>
      </div>
      <div class="columns">
        <reactome v-show="showReactome" id="metabolite-reactome" :model="model" :metaboliteID="metaboliteID" 
        :disableBut="this.relatedMetabolites.length == 0"></reactome>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Reactome from 'components/explorer/gemBrowser/Reactome';
import { chemicalFormula } from '../../../helpers/chemical-formatters';
import { reformatTableKey, reformatStringToLink, addMassUnit, idfy } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'metabolite',
  components: {
    Reactome,
  },
  props: ['model'],
  data() {
    return {
      messages,
      mId: this.$route.params.id,
      metaboliteID: '',
      mainTableKey: {
        human1: [
          { name: 'name' },
          { name: 'alt_name', display: 'Alternate name' },
          { name: 'aliases', display: 'Synonyms' },
          { name: 'description', display: 'Description' },
          { name: 'formula' },
          { name: 'charge' },
          { name: 'inchi' },
          { name: 'compartment' },
          { name: 'id' },
        ],
        yeast8: [
          { name: 'name' },
          { name: 'alt_name', display: 'Alternate name' },
          { name: 'aliases', display: 'Synonyms' },
          { name: 'description', display: 'Description' },
          { name: 'formula' },
          { name: 'charge' },
          { name: 'inchi' },
          { name: 'compartment' },
          { name: 'id' },
        ],
      },
      externalIDTableKey: {
        human1: [
          { name: 'hmdb_id', display: 'HMDB', link: 'hmdb_link' },
          { name: 'chebi_id', display: 'Chebi', link: 'chebi_link' },
          { name: 'mnxref_id', display: 'Mnxref', link: 'mnxref_link' },
        ],
        yeast8: [
        ],
      },
      metabolite: {},
      relatedMetabolites: [],
      errorMessage: '',
      activePanel: 'table',
      showReactome: false,
    };
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
  computed: {
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model.database_name]) {
        if (this.metabolite[item.name] && this.metabolite[item.link]) {
          return true;
        }
      }
      return false;
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
        this.metaboliteID = this.mId;
        this.metabolite = response.data;
        this.showReactome = true;
        this.getRelatedMetabolites();
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
        this.showReactome = false;
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
