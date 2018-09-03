<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-3">Reaction</h3>
      </div>
    </div>
    <div class="columns" v-show="showLoader">
      <loader></loader>
    </div>
    <div class="columns" v-show="!showLoader">
      <div class="reaction-table column is-10">
        <table v-if="reaction && Object.keys(reaction).length != 0" class="table main-table is-fullwidth">
          <tr v-for="el in mainTableKey[model]">
            <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
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
            <td v-else> - </td>
          </tr>
        </table>
        <h4 class="title is-4">references</h4>
        <table v-if="pmids && Object.keys(pmids).length != 0" id="main-table" class="table">
          <tr v-for="ref in reformatRefs(pmids)">
            <a :href="ref.link">
              <td v-if="ref.title" class="td-key has-background-primary has-text-white-bis">{{ ref.pmid }}</td>
              <td v-if="ref.formatted">{{ ref.formatted }}</td>
            </a>
          </tr>
        </table>
        <div v-else>No references found</div>
      </div>
      <div class="column">
        <div class="box has-text-centered">
          <div class="button is-info">
            <p><i class="fa fa-eye"></i> on Metabolic Viewer</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import Loader from 'components/Loader';
import { default as EventBus } from '../../../event-bus';
import { chemicalFormula, chemicalName, chemicalNameExternalLink, chemicalReaction } from '../../../helpers/chemical-formatters';
import { reformatTableKey, addMassUnit, reformatSBOLink, reformatECLink } from '../../../helpers/utils';

export default {
  name: 'reaction',
  props: ['model'],
  components: {
    Loader,
  },
  data() {
    return {
      rId: this.$route.params.id,
      mainTableKey: {
        hmr2: [
          { name: 'id', display: 'Model&nbsp;ID' },
          { name: 'equation', modifier: this.reformatEquation },
          { name: 'is_reversible', display: 'Reversible', isComposite: true, modifier: this.reformatReversible },
          { name: 'quantitative', isComposite: true, modifier: this.reformatQuant },
          { name: 'gene_rule', isComposite: true, display: 'Enzymes', modifier: this.reformatModifiers },
          { name: 'ec', display: 'EC', modifier: this.reformatECLink },
          { name: 'compartment', isComposite: true, modifier: this.reformatCompartment },
          { name: 'subsystem', display: 'Subsystem', modifier: this.reformatSubsystemList },
          { name: 'sbo_id', display: 'SBO', modifier: this.reformatSBOLink },
        ],
      },
      reaction: {},
      pmids: [],
      errorMessage: '',
      showLoader: true,
    };
  },
  created() {
    $('body').on('click', 'a.e', function f() {
      EventBus.$emit('GBnavigateTo', 'enzyme', $(this).attr('name'));
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
  methods: {
    setup() {
      this.rId = this.$route.params.id;
      this.load();
    },
    load() {
      axios.get(`${this.model}/reactions/${this.rId}/`)
      .then((response) => {
        this.showLoader = false;
        this.reaction = response.data.reaction;
        this.pmids = response.data.pmids;
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
      });
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    reformatEquation() { return this.$parent.$parent.reformatChemicalReactionLink(this.reaction); },
    reformatSBOLink(s, link) { return reformatSBOLink(s, link); },
    reformatECLink(s) { return reformatECLink(s); },
    reformatMass(s) { return addMassUnit(s); },
    reformatModifiers() {
      let newGRnameArr = null;
      if (this.reaction.name_gene_rule) {
        newGRnameArr = this.reaction.name_gene_rule.split(/ and | or /).map(
        e => e.replace(/^\(+|\)+$/g, '')
        );
      }

      let newGR = this.reaction.gene_rule;
      if (newGR) {
        const newGRArr = newGR.split(/ and | or /).map(
          e => e.replace(/^\(+|\)+$/g, '')
          );
        for (let i = 0, l = newGRArr.length; i < l; i += 1) {
          let e;
          if (newGRnameArr) {
            e = `<span class="tag"><a class="e is-size-6" name="${newGRArr[i]}">${newGRnameArr[i]}</a></span>`;
          } else {
            e = `<span class="tag"><a class="e is-size-6" name="${newGRArr[i]}">${newGRArr[i]}</a></span>`;
          }
          newGR = newGR.replace(newGRArr[i], e);
        }
      }
      return newGR;
    },
    reformatSubsystemList(substr) {
      let str = '';
      for (const s of substr.split('; ')) {
        str = str.concat(`<a class="s" name="${s}">`, s, '</a>');
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
            data.push(this.reformatMass(this.reaction[key]));
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
        chemicalReaction(this.reaction.compartment, this.reaction.is_reversible);
      if (this.reaction.is_transport) {
        return `${compartmentEq} (transport reaction)`;
      }
      return `${compartmentEq}`;
    },
    reformatReversible() { return this.reaction.is_reversible ? 'Yes' : 'No'; },
    reformatRefs(refs) {
      const outrefs = [];
      for (const key of Object.keys(refs)) {
        const formattedref = {};
        const ref = refs[key];
        formattedref.pmid = key;
        formattedref.link = `http://pubmed.com/${key}`;
        const text = [];
        if (ref.pubdate) {
          ref.pubyear = ref.pubdate.substring(0, 4);
        }
        const fields = ['sortfirstauthor', 'lastauthor', 'pubyear', 'fulljournalname', 'title'];
        for (const field of fields) {
          if (ref[field]) {
            text.push(ref[field]);
          }
        }
        formattedref.formatted = text.join(', ');
        outrefs.push(formattedref);
      }
      return outrefs;
    },
    chemicalFormula,
    chemicalName,
    chemicalNameExternalLink,
  },
};
</script>

<style lang="scss">
</style>