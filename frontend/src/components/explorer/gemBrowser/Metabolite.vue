<template>
  <div id="metabolite-page">
    <div v-if="componentNotFound" class="columns is-centered">
      <notFound :type="type" :component-id="mId"></notFound>
    </div>
    <div v-else>
      <div class="columns">
        <div class="column">
          <h3 class="title is-3">
            <span class="is-capitalized">{{ type }}</span> {{ metabolite.name }}
            <span v-if="metabolite && metabolite.compartment" class="is-size-5 has-text-grey">
              {{ metabolite.compartment.id }}</span>
          </h3>
        </div>
      </div>
      <div class="columns is-multiline metabolite-table is-variable is-8">
        <div class="column is-10-widescreen is-9-desktop is-full-tablet">
          <table v-if="metabolite" class="table main-table is-fullwidth">
            <tr v-for="el in mainTableKey" :key="el.name">
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
                <span v-else-if="el.name === 'compartment' && metabolite[el.name]">
                  <!-- eslint-disable-next-line max-len -->
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${metabolite[el.name].id}` }"
                  >{{ metabolite[el.name].name }}</router-link>
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
                <span v-for="(rm, i) in relatedMetabolites" :key="rm.id">
                  <br v-if="i !== 0">
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/metabolite/${rm.id}`}">
                    {{ rm.full_name }}
                  </router-link> in {{ rm.compartment_str }}
                </span>
              </td>
            </tr>
          </table>
          <ExtIdTable :type="type" :external-dbs="metabolite.external_databases"></ExtIdTable>
        </div>
        <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
          <router-link class="button is-info is-fullwidth is-outlined"
                       :to="{path: `/explore/interaction/${model.database_name}/${mId}`}">
            <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
            <span>{{ messages.interPartName }}</span>
          </router-link>
          <gem-contact :id="mId" :type="type" />
        </div>
      </div>
      <div class="columns">
        <reactome v-show="showReactome" id="metabolite-reactome" :metabolite-i-d="metaboliteID"
                  :disable-but="relatedMetabolites.length === 0">
        </reactome>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import Reactome from '@/components/explorer/gemBrowser/Reactome';
import GemContact from '@/components/shared/GemContact';
import NotFound from '@/components/NotFound';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import { chemicalFormula } from '../../../helpers/chemical-formatters';
import { reformatTableKey } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'Metabolite',
  components: {
    NotFound,
    ExtIdTable,
    Reactome,
    GemContact,
  },
  data() {
    return {
      messages,
      mId: this.$route.params.id,
      type: 'metabolite',
      metaboliteID: '',
      mainTableKey: [
        { name: 'id' },
        { name: 'name' },
        { name: 'alternate_name', display: 'Alternate name' },
        { name: 'synonyms' },
        { name: 'description' },
        { name: 'formula' },
        { name: 'charge' },
        { name: 'inchi', display: 'InChI' },
        { name: 'compartment' },
      ],
      metabolite: {},
      relatedMetabolites: [],
      componentNotFound: false,
      activePanel: 'table',
      showReactome: false,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
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
    chemicalFormula,
  },
};
</script>

<style lang="scss"></style>
