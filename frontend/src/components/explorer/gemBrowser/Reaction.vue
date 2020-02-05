<template>
  <div v-if="componentNotFound" class="columns is-centered">
    <notFound component="reaction" :component-id="rId"></notFound>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-size-3">Reaction {{ reaction.id }}</h3>
      </div>
    </div>
    <div v-show="showLoader" class="columns">
      <loader></loader>
    </div>
    <div v-show="!showLoader" class="columns is-multiline is-variable is-8">
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
            <td v-if="'isComposite' in el">
              <span v-html="el.modifier()"></span>
            </td>
            <td v-else-if="el.name === 'ec' && reaction[el.name]">
              <!-- eslint-disable-next-line max-len -->
              <router-link v-for="eccode in reaction[el.name].split('; ')" :key="eccode" :to="{ name: 'search', query: { term: eccode }}">
                {{ eccode }}
              </router-link>
            </td>
            <td v-else-if="reaction[el.name]">
              <template v-if="'modifier' in el" v-html="el.modifier(reaction[el.name])"></template>
              <template v-else-if="el.name === 'subsystem'">
                <template v-for="(v, i) in reaction[el.name]">
                  <template v-if="i !== 0">; </template>
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/subsystem/${v.id}` }"> {{ v.name }}</router-link>
                </template>
              </template>
              <template v-else-if="el.name === 'compartment'">
                <template v-for="(v, i) in reaction[el.name]">
                  <template v-if="i !== 0">; </template>
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${v.id}` }"> {{ v.name }}</router-link>
                </template>
                <template v-if="reaction.is_transport">
                  (transport reaction)
                </template>
              </template>
              <template v-else>{{ reaction[el.name] }}</template>
            </td>
            <td v-else-if="el.name === 'equation'">
              <span v-html="el.modifier(reaction[el.name])"></span>
            </td>
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
        <ExtIdTable :component-type="'reaction'" :external-dbs="reaction.external_databases"></ExtIdTable>
        <h4 class="title is-size-4">References via PubMed ID</h4>
        <table class="main-table table is-fullwidth">
          <template v-if="unformattedRefs.length === 0">
            <p>This reaction has no associated references.</p>
          </template>
          <template v-else>
            <tr v-for="oneRef in unformattedRefs" :key="oneRef.pmid">
              <td class="td-key has-background-primary has-text-white-bis">{{ oneRef.pmid }}</td>
              <template v-if="formattedRefs[oneRef.pmid]">
                <td v-for="refData in [formattedRefs[oneRef.pmid]]" :key="refData.id">
                  <a :href="refData.link" target="_blank">
                    <template v-for="author in refData.authors">
                      {{ author }},
                    </template>
                    {{ refData.year }}. <i>{{ refData.title }}</i>
                    {{ refData.journal }}
                  </a>
                </td>
              </template>
              <template v-else>
                <td></td>
              </template>
            </tr>
          </template>
        </table>
      </div>
      <div class="column is-2-widescreen is-3-desktop is-half-tablet has-text-centered">
        <maps-available :id="rId" :model="model" :type="'reaction'" :element-i-d="rId"></maps-available>
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
import { default as EventBus } from '../../../event-bus';
import { reformatTableKey, addMassUnit, reformatCompEqString, reformatChemicalReactionHTML, reformatEqSign } from '../../../helpers/utils';

export default {
  name: 'Reaction',
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    ExtIdTable,
  },
  props: {
    model: Object,
  },
  data() {
    return {
      rId: this.$route.params.id,
      mainTableKey: [
        { name: 'id' },
        { name: 'equation', modifier: this.reformatEquation },
        { name: 'is_reversible', display: 'Reversible', isComposite: true, modifier: this.reformatReversible },
        { name: 'quantitative', isComposite: true, modifier: this.reformatQuant },
        { name: 'gene_rule', isComposite: true, display: 'Gene rule', modifier: this.reformatGenes },
        { name: 'ec', display: 'EC' },
        { name: 'compartment', display: 'Compartment(s)' },
        { name: 'subsystem', display: 'Subsystem(s)' },
      ],
      reaction: {},
      relatedReactions: [],
      errorMessage: '',
      showLoader: true,
      mapsAvailable: {},
      unformattedRefs: [],
      formattedRefs: {},
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
            this.unformattedRefs = response.data.pmids;
            this.reformatRefs();
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
    reformatRefs() {
      this.formattedRefs = {};
      const queryIDs = `(EXT_ID:"${this.unformattedRefs.map(e => e.pmid).join('"+OR+EXT_ID:"')}")`;
      axios.get(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=${queryIDs}&resultType=core&format=json`)
        .then((response) => {
          const newFormattedRefs = {};
          response.data.resultList.result.forEach((details) => {
            try {
              const refDetails = {};
              refDetails.link = details.fullTextUrlList.fullTextUrl
                .filter(e => e.documentStyle === 'html' && e.site === 'Europe_PMC');
              if (refDetails.link.length === 0) {
                refDetails.link = details.fullTextUrlList.fullTextUrl.filter(
                  e => e.documentStyle === 'doi' || e.documentStyle === 'abs')[0].url;
              } else {
                refDetails.link = refDetails.link[0].url;
              }
              if (details.pubYear) {
                refDetails.year = details.pubYear;
              }
              refDetails.authors = details.authorList.author.map(e => e.fullName);
              refDetails.journal = details.journalInfo.journal.title;
              refDetails.title = details.title;
              newFormattedRefs[details.id] = refDetails;
            } catch (e) {
            // pass
            }
          });
          this.formattedRefs = newFormattedRefs;
        })
        .catch(() => {
        });
    },
    reformatTableKey,
    reformatCompEqString,
    reformatChemicalReactionHTML,
    reformatEqSign,
  },
};
</script>

<style lang="scss"></style>
