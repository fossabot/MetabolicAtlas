<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-size-3">Reaction {{ reaction.id }}</h3>
      </div>
    </div>
    <div class="columns" v-show="showLoader">
      <loader></loader>
    </div>
    <div class="columns is-multiline is-variable is-8" v-show="!showLoader">
      <div class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
        <table v-if="reaction && Object.keys(reaction).length != 0" class="table main-table is-fullwidth">
          <tr v-for="el in mainTableKey[model.database_name]">
            <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
            <td v-else-if="el.name == 'id'" class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
            <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
            <td v-if="'isComposite' in el">
              <span v-html="el.modifier()"></span>
            </td>
            <td v-else-if="reaction[el.name]">
              <span v-if="'modifier' in el" v-html="el.modifier(reaction[el.name])">
              </span>
              <span v-else>
                {{ reaction[el.name] }}
              </span>
            </td>
            <td v-else-if="el.name === 'equation'">
              <span v-html="el.modifier(reaction[el.name])">
              </span>
            </td>
            <td v-else> - </td>
          </tr>
          <tr v-if="relatedReactions.length !== 0">
            <td class="td-key has-background-primary has-text-white-bis">Related reaction(s)</td>
            <td>
              <template v-for="(rr, i) in relatedReactions">
                <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/reaction/${rr.id}`}">
                  {{ rr.id }}
                </router-link>
                <div style="margin-left: 30px">
                  <span v-html="reformatChemicalReactionHTML(rr, true)"></span>
                  (<span v-html="reformatEqSign(rr.compartment, rr.is_reversible)">
                  </span>)
                </div>
              </template>
            </td>
          </tr>
        </table>
        <template v-if="hasExternalID">
          <h4 class="title is-4">External databases</h4>
          <table v-if="reaction && Object.keys(reaction).length != 0" id="ed-table" class="table is-fullwidth">
            <tr v-for="el in externalIDTableKey[model.database_name]" v-if="reaction[el.name] && reaction[el.link]">
              <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
              <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
              <td>
                <a :href="`${reaction[el.link]}`" target="_blank">{{ reaction[el.name] }}</a>
              </td>
            </tr>
          </table>
        </template>
        <template v-if="formattedRef.length !== 0">
          <h4 class="title is-size-4">PMID References</h4>
          <table class="main-table table">
            <tr v-for="oneRef in formattedRef">
              <td v-if="oneRef.title" class="td-key has-background-primary has-text-white-bis">{{ oneRef.pmid }}</td>
                <td>
                  <a :href="oneRef.link" target="_blank">
                    <template v-for="author in oneRef.authors">
                      {{ author }},
                    </template>
                    {{ oneRef.year }}. <i>{{ oneRef.title }}</i>
                    {{ oneRef.journal }}
                  </a>
                </td>
            </tr>
          </table>
        </template>
        <template v-else-if="this.reaction.pmids && this.reaction.pmids.length === 0">
          <p>No PMID references found</p>
        </template>
      </div>
      <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
        <maps-available :model="model" :type="'reaction'" :id="rId" :elementID="rId"></maps-available>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import Loader from '@/components/Loader';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import { default as EventBus } from '../../../event-bus';
import { reformatTableKey, addMassUnit, reformatECLink, reformatCompEqString, reformatChemicalReactionHTML, reformatEqSign } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'reaction',
  props: ['model'],
  components: {
    Loader,
    MapsAvailable,
  },
  data() {
    return {
      messages,
      rId: this.$route.params.id,
      mainTableKey: {
        human1: [
          { name: 'id' },
          { name: 'equation', modifier: this.reformatEquation },
          { name: 'is_reversible', display: 'Reversible', isComposite: true, modifier: this.reformatReversible },
          { name: 'quantitative', isComposite: true, modifier: this.reformatQuant },
          { name: 'gene_rule', isComposite: true, display: 'Genes', modifier: this.reformatGenes },
          { name: 'ec', display: 'EC', modifier: this.reformatECLink },
          { name: 'compartment', isComposite: true, modifier: this.reformatCompartment },
          { name: 'subsystem_str', display: 'Subsystem', modifier: this.reformatSubsystemList },
        ],
        yeast8: [
          { name: 'id' },
          { name: 'equation', modifier: this.reformatEquation },
          { name: 'is_reversible', display: 'Reversible', isComposite: true, modifier: this.reformatReversible },
          { name: 'quantitative', isComposite: true, modifier: this.reformatQuant },
          { name: 'gene_rule', isComposite: true, display: 'Genes', modifier: this.reformatGenes },
          { name: 'ec', display: 'EC', modifier: this.reformatECLink },
          { name: 'compartment', isComposite: true, modifier: this.reformatCompartment },
          { name: 'subsystem_str', display: 'Subsystem', modifier: this.reformatSubsystemList },
        ],
      },
      externalIDTableKey: {
        human1: [
          { name: 'kegg_id', display: 'KEGG', link: 'kegg_link' },
          { name: 'bigg_id', display: 'BiGG', link: 'bigg_link' },
          { name: 'reactome_id', display: 'Reactome', link: 'reactome_link' },
          { name: 'metanetx_id', display: 'MetaNetX', link: 'metanetx_link' },
        ],
        yeast8: [],
      },
      reaction: {},
      relatedReactions: [],
      errorMessage: '',
      showLoader: true,
      mapsAvailable: {},
      formattedRef: [],
    };
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
  computed: {
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model.database_name]) {
        if (this.reaction[item.name] && this.reaction[item.link]) {
          return true;
        }
      }
      return false;
    },
  },
  methods: {
    setup() {
      this.rId = this.$route.params.id;
      this.load();
    },
    load() {
      axios.get(`${this.model.database_name}/get_reaction/${this.rId}/`)
      .then((response) => {
        this.showLoader = false;
        this.reaction = response.data.reaction;
        if (response.data.pmids.length !== 0) {
          this.reformatRefs(response.data.pmids);
        }
        this.getRelatedReactions();
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
      });
    },
    getRelatedReactions() {
      axios.get(`${this.model.database_name}/get_reaction/${this.rId}/related`)
      .then((response) => {
        this.relatedReactions = response.data;
        this.relatedReactions.sort((a, b) => (a.compartment < b.compartment ? -1 : 1));
      })
      .catch(() => {
        this.relatedReactions = [];
      });
    },
    reformatEquation() { return reformatChemicalReactionHTML(this.reaction); },
    reformatGenes() {
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
    reformatSubsystemList(substr) {
      let str = '';
      for (const s of substr.split('; ')) {
        str = str.concat(`<a class="s" name="${s}">`, s, '</a><br>');
      }
      if (str) {
        str = str.slice(0, -4);
      }
      return str;
    },
    formatQuantFieldName(name) { return `${name}:&nbsp;`; },
    reformatQuant() {
      const data = [];
      for (const key of ['lower_bound', 'upper_bound', 'objective_coefficient']) {
        if (this.reaction[key] != null) {
          data.push(this.formatQuantFieldName(this.reformatTableKey(key)));
          if (key === 'objective_coefficient') {
            data.push(addMassUnit(this.reaction[key]));
          } else {
            data.push(this.reaction[key]);
          }
          data.push('<span>&nbsp;&dash;&nbsp;</span>');
        }
      }
      let s = data.join(' ');
      if (s.endsWith('<span>&nbsp;&dash;&nbsp;</span>')) {
        s = s.slice(0, -31);
      }
      return s;
    },
    reformatCompartment() {
      const compartmentEq =
        this.reformatCompEqString(this.reaction.compartment, this.reaction.is_reversible);
      if (this.reaction.is_transport) {
        return `${compartmentEq} (transport reaction)`;
      }
      return `${compartmentEq}`;
    },
    reformatReversible() { return this.reaction.is_reversible ? 'Yes' : 'No'; },
    reformatRefs(refs) {
      const queryIDs = `(EXT_ID:"${refs.map(e => e.pmid).join('"+OR+EXT_ID:"')}")`;
      axios.get(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=${queryIDs}&resultType=core&format=json`)
      .then((response) => {
        for (const details of response.data.resultList.result) {
          try {
            const newRef = {};
            newRef.pmid = details.id;
            newRef.link = details.fullTextUrlList.fullTextUrl.filter(e => e.documentStyle === 'html' && e.site === 'Europe_PMC');
            if (newRef.link.length === 0) {
              newRef.link = details.fullTextUrlList.fullTextUrl.filter(
                e => e.documentStyle === 'doi' || e.documentStyle === 'abs')[0].url;
            } else {
              newRef.link = newRef.link[0].url;
            }
            if (details.pubYear) {
              newRef.year = details.pubYear;
            }
            newRef.authors = details.authorList.author.map(e => e.fullName);
            newRef.journal = details.journalInfo.journal.title;
            newRef.title = details.title;
            this.formattedRef.push(newRef);
          } catch (e) {
            // pass
          }
        }
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
      });
    },
    viewReactionOnMap(reactionID) {
      EventBus.$emit('viewReactionOnMap', reactionID);
    },
    reformatTableKey,
    reformatECLink,
    reformatCompEqString,
    reformatChemicalReactionHTML,
    reformatEqSign,
  },
};
</script>

<style lang="scss"></style>
