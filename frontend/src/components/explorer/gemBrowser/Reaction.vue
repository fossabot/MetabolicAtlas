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
    <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
    <div v-else class="columns is-multiline is-variable is-8">
      <div class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
        <div class="table-container">
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
                  <div class="tags">
                    <template v-for="c in reaction[el.name]">
                      <span :key="c.id" class="tag">
                        <!-- eslint-disable-next-line max-len -->
                        <router-link :to="{ name: 'browser', params: { model: model.database_name, type: 'compartment', id: c.id } }">{{ c.name }}</router-link>
                      </span>
                    </template>
                    <template v-if="reaction.is_transport">
                      &nbsp;(transport reaction)
                    </template>
                  </div>
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
                  <!-- eslint-disable-next-line max-len -->
                  <router-link :to="{ name: 'browser', params: { model: model.database_name, type: 'reaction', id: rr.id } }">
                    {{ rr.id }}
                  </router-link>
                  <div style="margin-left: 30px">
                    <span v-html="reformatChemicalReactionHTML(rr, true, model.database_name)"></span>
                    (<span v-html="reformatEqSign(rr.compartment_str, rr.is_reversible)">
                    </span>)
                  </div>
                </span>
              </td>
            </tr>
          </table>
        </div>
        <ExtIdTable :type="type" :external-dbs="reaction.external_databases"></ExtIdTable>
        <references :reference-list="referenceList" />
      </div>
      <div class="column is-2-widescreen is-3-desktop is-half-tablet has-text-centered">
        <maps-available :id="rId" :type="type" :viewer-selected-i-d="reaction.id" />
        <gem-contact :id="rId" :type="type" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import Loader from '@/components/Loader';
import NotFound from '@/components/NotFound';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import GemContact from '@/components/shared/GemContact';
import References from '@/components/shared/References';
import { buildCustomLink, reformatTableKey, addMassUnit, reformatChemicalReactionHTML, reformatEqSign } from '@/helpers/utils';

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
      errorMessage: '',
      showLoaderMessage: '',
      mapsAvailable: {},
      componentNotFound: false,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      reaction: state => state.reactions.reaction,
      referenceList: state => state.reactions.referenceList,
      relatedReactions: state => state.reactions.relatedReactions,
    }),
  },
  watch: {
    $route() {
      this.setup();
    },
  },
  beforeMount() {
    this.setup();
  },
  methods: {
    async setup() {
      this.showLoaderMessage = 'Loading reaction data';
      this.rId = this.$route.params.id;
      try {
        const payload = { model: this.model.database_name, id: this.rId };
        await this.$store.dispatch('reactions/getReactionData', payload);
        this.componentNotFound = false;
        this.showLoaderMessage = '';
        await this.getRelatedReactions();
      } catch {
        this.componentNotFound = true;
        document.getElementById('search').focus();
      }
    },
    async getRelatedReactions() {
      try {
        const payload = { model: this.model.database_name, id: this.rId };
        await this.$store.dispatch('reactions/getRelatedReactionsForReaction', payload);
      } catch {
        this.$store.dispatch('reactions/clearRelatedReactions');
      }
    },
    reformatEquation() { return reformatChemicalReactionHTML(this.reaction, false, this.model.database_name); },
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
            const customLink = buildCustomLink({ model: this.model.database_name, type: 'gene', id: newE, title: tag });
            return `${prefix}<span class="tag">${customLink}</span>${suffix}`;
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
    reformatChemicalReactionHTML,
    reformatEqSign,
  },
};
</script>

<style lang="scss"></style>
