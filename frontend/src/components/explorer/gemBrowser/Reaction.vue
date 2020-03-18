<template>
  <div v-if="componentNotFound" class="columns is-centered">
    <notFound :type="type" :component-id="rId"></notFound>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-size-3"><span class="is-capitalized">{{ type }}</span> {{ reaction.id }}</h3>
      </div>
    </div>
    <div v-if="showLoader" class="columns">
      <loader></loader>
    </div>
    <div v-else class="columns is-multiline is-variable is-8">
      <div class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
        <table v-if="reaction && Object.keys(reaction).length !== 0" class="table main-table is-fullwidth">
          <tr v-for="el in mainTableKey" :key="el.name">
            <td v-if="'display' in el"
                class="td-key has-background-primary has-text-white-bis"
                v-html="el.display"></td>
            <td v-else-if="el.name === 'id'"
                class="td-key has-background-primary has-text-white-bis">
              {{ model.short_name }} ID</td>
            <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
            <td v-if="reaction[el.name]">
              <template v-if="'modifier' in el"><span v-html="el.modifier()"></span></template>
              <template v-else-if="el.name === 'subsystem'">
                <template v-for="(v, i) in reaction[el.name]">
                  <template v-if="i !== 0">; </template>
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                  <router-link :to="{ name: 'browser', params: { model: model.database_name, type: 'subsystem', id: v.id } }"> {{ v.name }}</router-link>
                </template>
              </template>
              <template v-else-if="el.name === 'compartment'">
                <template v-for="(v, i) in reaction[el.name]">
                  <template v-if="i !== 0">; </template>
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                  <router-link :to="{ name: 'browser', params: { model: model.database_name, type: 'compartment', id: v.id } }"> {{ v.name }}</router-link>
                </template>
                <template v-if="reaction.is_transport">
                  (transport reaction)
                </template>
              </template>
              <template v-else-if="el.name === 'ec'">
                <!-- eslint-disable-next-line max-len -->
                <router-link v-for="eccode in reaction[el.name].split('; ')" :key="eccode" :to="{ name: 'search', query: { term: eccode }}">
                  {{ eccode }}
                </router-link>
              </template>
              <template v-else>{{ reaction[el.name] }}</template>
            </td>
            <td v-else-if="'modifier' in el"><span v-html="el.modifier()"></span></td>
            <td v-else> - </td>
          </tr>
          <tr v-if="relatedReactions.length !== 0">
            <td class="td-key has-background-primary has-text-white-bis">Related reaction(s)</td>
            <td>
              <span v-for="rr in relatedReactions" :key="rr.id">
                <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/reaction/${rr.id}`}">
                  {{ rr.id }}
                </router-link>
                <div style="margin-left: 30px">
                  <span v-html="reformatChemicalReactionHTML(rr, true)"></span>
                  (<span v-html="reformatEqSign(rr.compartment_str, rr.is_reversible)">
                  </span>)
                </div>
              </span>
            </td>
          </tr>
        </table>
        <ExtIdTable :type="type" :external-dbs="reaction.external_databases"></ExtIdTable>
        <br>
        <references :reference-list="referenceList" />
      </div>
      <div class="column is-2-widescreen is-3-desktop is-half-tablet has-text-centered">
        <maps-available :id="rId" :model="model" :type="type" :element-i-d="rId"></maps-available>
        <gem-contact :id="rId" :model="model" :type="type" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import Loader from '@/components/Loader';
import NotFound from '@/components/NotFound';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import GemContact from '@/components/shared/GemContact';
import References from '@/components/shared/References';
import { default as EventBus } from '@/event-bus';
import { reformatTableKey, addMassUnit, reformatCompEqString, reformatChemicalReactionHTML, reformatEqSign } from '@/helpers/utils';

export default {
  name: 'Reaction',
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    GemContact,
    ExtIdTable,
    References,
  },
  props: {
    model: Object,
  },
  data() {
    return {
      rId: this.$route.params.id,
      type: 'reaction',
      mainTableKey: [
        { name: 'id' },
        { name: 'equation', modifier: this.reformatEquation },
        { name: 'is_reversible', display: 'Reversible', modifier: this.reformatReversible },
        { name: 'quantitative', modifier: this.reformatQuant },
        { name: 'gene_rule', display: 'Gene rule', modifier: this.reformatGenes },
        { name: 'ec', display: 'EC' },
        { name: 'compartment', display: 'Compartment(s)' },
        { name: 'subsystem', display: 'Subsystem(s)' },
      ],
      reaction: {},
      relatedReactions: [],
      errorMessage: '',
      showLoader: true,
      mapsAvailable: {},
      referenceList: [],
      componentNotFound: false,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/reaction/')) {
        if (this.rId !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  created() {
    $('body').on('click', 'a.e', function f() {
      EventBus.$emit('GBnavigateTo', 'gene', $(this).attr('name'));
    });
    $('body').on('click', 'a.s', function f() {
      EventBus.$emit('GBnavigateTo', 'subsystem', $(this).attr('name'));
    });
  },
  beforeMount() {
    this.setup();
  },
  methods: {
    setup() {
      this.rId = this.$route.params.id;
      this.load();
    },
    load() {
      axios.get(`${this.model.database_name}/get_reaction/${this.rId}/`)
        .then((response) => {
          this.componentNotFound = false;
          this.showLoader = false;
          this.reaction = response.data.reaction;
          if (response.data.pmids.length !== 0) {
            this.referenceList = response.data.pmids;
          }
          this.getRelatedReactions();
        })
        .catch(() => {
          this.componentNotFound = true;
          document.getElementById('search').focus();
        });
    },
    getRelatedReactions() {
      axios.get(`${this.model.database_name}/get_reaction/${this.rId}/related`)
        .then((response) => {
          this.relatedReactions = response.data;
          this.relatedReactions.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
        })
        .catch(() => {
          this.relatedReactions = [];
        });
    },
    reformatEquation() { return reformatChemicalReactionHTML(this.reaction); },
    reformatGenes() {
      if (!this.reaction.gene_rule) {
        return '-';
      }
      let newGRnameArr = null;
      if (this.reaction.gene_rule_wname) {
        newGRnameArr = this.reaction.gene_rule_wname.split(/ +/).map(
          e => e.replace(/^\(+|\)+$/g, '')
        );
      }
      let newGR = this.reaction.gene_rule;
      if (newGR) {
        let i = -1;
        const newGRArr = newGR.split(/ +/).map(
          (e) => {
            i += 1;
            if (e === 'or' || e === 'and') {
              return e;
            }
            const prefix = e[0] === '(' ? '(' : '';
            const suffix = e.slice(-1) === ')' ? ')' : '';
            const newE = e.replace(/^\(+|\)+$/g, '');
            const tag = newGRnameArr ? newGRnameArr[i] : newE;
            return `${prefix}<span class="tag"><a class="e is-size-6" name="${newE}">${tag}</a></span>${suffix}`;
          });
        newGR = newGRArr.join(' ');
      }
      return newGR;
    },
    formatQuantFieldName(name) { return `${name}:&nbsp;`; },
    reformatQuant() {
      const data = [];
      ['lower_bound', 'upper_bound', 'objective_coefficient'].forEach((key) => {
        if (this.reaction[key] != null) {
          data.push(this.formatQuantFieldName(this.reformatTableKey(key)));
          if (key === 'objective_coefficient') {
            data.push(addMassUnit(this.reaction[key]));
          } else {
            data.push(this.reaction[key]);
          }
          data.push('<span>&nbsp;&dash;&nbsp;</span>');
        }
      });
      let s = data.join(' ');
      if (s.endsWith('<span>&nbsp;&dash;&nbsp;</span>')) {
        s = s.slice(0, -31);
      }
      return s;
    },
    reformatReversible() { return this.reaction.is_reversible ? 'Yes' : 'No'; },
    reformatTableKey,
    reformatCompEqString,
    reformatChemicalReactionHTML,
    reformatEqSign,
  },
};
</script>

<style lang="scss"></style>
