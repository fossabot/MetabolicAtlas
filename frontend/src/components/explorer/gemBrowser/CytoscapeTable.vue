<template>
  <div class="container cytoscape-table">
    <div class="columns">
      <div class="column" style="padding-bottom: 0">
        <cytoscape-table-search
          :reset="resetTable"
          @search="searchTable($event)"
          class="is-10"
        ></cytoscape-table-search>
      </div>
      <div class="column is-2" style="padding-bottom: 0">
        <div class="columns">
          <div class="column">
            <a @click="exportToTSV()" class="button is-primary is-pulled-right">
              Export to TSV
            </a>
          </div>
        </div>
      </div>
    </div>
    <div class="columns">
      <div class="column">
        <div class="field">
          <span class="tag">
             # Reaction(s): {{ filteredReactions.length }}
          </span>
          <span>
            &nbsp;
          </span>
          <span class="tag">
            # Unique Metabolite(s): {{ metaboliteCount }}
          </span>
          <span v-show="geneCount">
            &nbsp;
          </span>
          <span class="tag" v-show="geneCount">
             # Unique Gene(s): {{ geneCount }}
          </span>
          <span class="is-pulled-right" v-show="isGraphVisible">
             Click on a <span class="tag is-rounded"><span class="is-size-6">label</span></span> to highlight the corresponding element on the graph
          </span>
        </div>
        <table id="cytoTable" class="table is-bordered is-narrow is-fullwidth" ref="table">
          <thead>
            <tr style="background: #F8F4F4">
              <th class="is-unselectable clickable"
                v-for="s in columns"
                @click="sortBy(s.field)"
              >{{ s.display }}</th>
            </tr>
          </thead>
          <tbody id="machingTableBody" ref="machingTableBody">
            <tr v-for="r in matchingReactions">
              <td v-for="s in columns" v-if="'modifier' in s" v-html="applyModifier(s, r)"></td>
              <td v-else-if="s.field === 'id'">
                <template v-if="isGraphVisible">
                  <span class="tag is-rounded clickable" @click="HLreaction(r.id)" 
                  :class="[{ 'hl': isSelected(r.id) }, '']">
                    <span class="is-size-6">{{ r.id }}</span>
                  </span>
                </template>
                <template v-else>
                 {{ r.id }}
                </template>
              </td>
              <td v-else-if="['reactants', 'products', 'genes'].includes(s.field)">
                <template v-for="el in r[s.field]">
                  <span class="tag is-rounded clickable is-medium" :title="s.field !== 'genes' ? `${el.id} - ${el.compartment_str}` : el.id"
                    @click="highlight(el.id)" :class="[{ 'hl': isSelected(el.id) }, '']">
                    <span class="">{{ el.name || el.id }}</span>
                  </span>
                </template>
              </td>
              <td v-else>
                {{ r[s.field] }}
              </td>
            </tr>
          </tbody>
          <tbody id="unmachingTableBody" ref="unmachingTableBody">
            <tr v-for="r in unMatchingReactions">
              <td v-for="s in columns" v-if="'modifier' in s" v-html="applyModifier(s, r)"></td>
              <td v-else-if="s.field === 'id'">
                <span class="tag is-rounded clickable" @click="HLreaction(r.id)" 
                :class="[{ 'hl': isSelected(r.id) }, '']">
                  <span class="is-size-6">{{ r.id }}</span>
                </span>
              </td>
              <td v-else-if="['reactants', 'products', 'genes'].includes(s.field)">
                <template v-for="el in r[s.field]">
                  <span class="tag is-rounded clickable" :title="s.field !== 'genes' ? `${el.id} - ${el.compartment_str}` : el.id"
                    @click="highlight(el.id)" :class="[{ 'hl': isSelected(el.id) }, '']">
                    <span class="is-size-6">{{ el.name || el.id }}</span>
                  </span>&nbsp;
                </template>
              </td>
              <td v-else>
                {{ r[s.field] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>

import { default as FileSaver } from 'file-saver';
import CytoscapeTableSearch from '@/components/explorer/gemBrowser/CytoscapeTableSearch';
import { default as compare } from '../../../helpers/compare';
import { default as EventBus } from '../../../event-bus';
import { reformatEqSign } from '../../../helpers/utils';


export default {
  name: 'cytoscape-table',
  components: {
    CytoscapeTableSearch,
  },
  props: ['reactions', 'selectedElmId', 'selectedReactionId', 'isGraphVisible', 'filename', 'sheetname'],
  data() {
    return {
      columns: [
        { field: 'id', display: 'Reaction ID' },
        { field: 'reactants', display: 'Reactants' },
        { field: 'products', display: 'Products' },
        { field: 'genes', display: 'Genes' },
        { field: 'compartment', display: 'Compartment', modifier: this.reformatEqSign },
      ],
      sortedReactions: [],
      matchingReactions: [],
      unMatchingReactions: [],
      sortAsc: true,
      tableSearchTerm: '',
      errorMessage: '',
    };
  },
  watch: {
    reactions() {
      this.sortedReactions = this.filteredReactions;
      this.matchingReactions = this.sortedReactions;
    },
  },
  computed: {
    filteredReactions: function f() {
      return this.reactions.map(e => e);
    },
    geneCount() {
      const genes = new Set();
      for (const r of this.reactions) {
        r.genes.forEach((e) => { genes.add(e.id); });
      }
      return genes.size;
    },
    metaboliteCount() {
      const metabolites = new Set();
      for (const r of this.reactions) {
        r.reactants.forEach((e) => { metabolites.add(e.id); });
        r.products.forEach((e) => { metabolites.add(e.id); });
      }
      return metabolites.size;
    },
  },
  methods: {
    applyModifier(s, elm) { return s.modifier(elm[s.field], elm.link); },
    viewReactionComponent(type, id) { EventBus.$emit('GBnavigateTo', type, id); },
    isSelected(elmId) {
      return this.selectedElmId === elmId || this.selectedReactionId === elmId;
    },
    highlight(elmId) {
      const sameID = this.selectedElmId === elmId;
      if (this.isGraphVisible) {
        this.$emit('highlight', sameID ? '' : elmId);
      } else {
        this.selectedElmId = sameID ? '' : elmId; // avoid mutate prop
      }
    },
    HLreaction(rID) {
      this.$emit('HLreaction', this.selectedReactionId === rID ? null : rID);
    },
    resetTable() {
      this.sortedReactions = this.filteredReactions;
      this.tableSearchTerm = '';
      this.updateTable();
    },
    searchTable(term) {
      this.tableSearchTerm = term;
      this.updateTable();
    },
    sortBy(field) {
      const reactions = Array.prototype.slice
        .call(this.filteredReactions); // Do not mutate original elms;
      this.sortedReactions = reactions.sort(compare(field, null, this.sortAsc ? 'asc' : 'desc'));
      this.sortAsc = !this.sortAsc;
      this.updateTable();
    },
    updateTable() {
      if (this.tableSearchTerm === '') {
        this.matchingReactions = this.sortedReactions;
        this.unMatchingReactions = [];
        this.$refs.machingTableBody.style.display = '';
      } else {
        this.matchingReactions = [];
        this.unMatchingReactions = [];
        const t = this.tableSearchTerm.toLowerCase();
        for (const elm of this.sortedReactions) {
          let matches = false;
          for (const s of this.columns) {
            const val = elm[s.field];
            if (typeof val === 'object' && ['reactants', 'products', 'genes'].includes(s.field)) {
              let match = false;
              for (const el of val) {
                for (const k of Object.keys(el)) {
                  if (k === 'id') {
                    match = el[k].toLowerCase() === t;
                  } else {
                    match = el[k].toLowerCase().includes(t);
                  }
                  if (match) {
                    matches = match;
                    break;
                  }
                }
                if (matches) {
                  break;
                }
              }
            } else if (!matches && val && val.toLowerCase().includes(t)) {
              matches = true;
              break;
            }
          }

          if (matches) {
            this.matchingReactions.push(elm);
          } else {
            this.unMatchingReactions.push(elm);
          }
        }
        // fix disappearing row/cell borders
        if (this.matchingReactions.length === 0) {
          this.$refs.machingTableBody.style.display = 'none';
        } else {
          this.$refs.machingTableBody.style.display = '';
        }
      }
    },
    exportToTSV() {
      try {
        let tsvContent = `${this.columns.map(e => e.display).join('\t')}\n`;
        tsvContent += this.sortedReactions.map(d => [
          d.id,
          d.reactants.map(e => e.name || e.id).join('; '),
          d.products.map(e => e.name || e.id).join('; '),
          d.genes.map(e => e.name || e.id).join('; '),
          d.compartment,
        ].join('\t')
        ).join('\n');
        const blob = new Blob([tsvContent], {
          type: 'text/tsv;charset=utf-8',
        });
        FileSaver.saveAs(blob, `${this.filename}.tsv`);
      } catch (_) {
        // this.errorMessage = e;
      }
    },
    reformatEqSign,
  },
};

</script>

<style lang="scss">

.cytoscape-table {
  #unmachingTableBody {
    opacity: 0.3;
  }

  sup {
    vertical-align: bottom;
    font-size: 0.7em;

    &.top {
      vertical-align: top;
    }
  }
}

</style>
