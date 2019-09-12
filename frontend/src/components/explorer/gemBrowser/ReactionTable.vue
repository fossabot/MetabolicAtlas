<template>
  <div class="reaction-table">
    <div class="field">
      <span class="tag is-medium" :class="reactions.length == limit ? 'is-warning' : ''">
        # Reactions: {{ reactions.length }}
      </span>
      <template v-if="transportReactionCount !== 0">
        &nbsp;including&nbsp;
        <span class="tag is-medium clickable" @click="sortTable('is_transport', null, 'desc')">
          {{ transportReactionCount }} transport reactions
        </span>
      </template>
      <span v-show="reactions.length == limit" class="tag is-medium is-warning is-pulled-right">
        The number of reactions displayed is limited to {{ limit }}.
      </span>
    </div>
    <table ref="table" class="table is-bordered is-striped is-narrow is-fullwidth">
      <thead>
        <tr class="has-background-white-ter">
          <th v-for="f in fields"
              v-show="showCol(f.name)"
              :key="f.name"
              class="is-unselectable clickable"
              :title="`Sort by ${f.display}`"
              @click="sortTable(f.name, null, null)">
            {{ f.display.replace(' ', '&nbsp;') }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in sortedReactions" :key="r.id">
          <td>
            <router-link
              :to="{ path: `/explore/gem-browser/${model.database_name}/reaction/${r.id}` }"
            >{{ r.id }}</router-link>
          </td>
          <td v-html="getReformatChemicalReactionHTML(r)"></td>
          <td>
            <!-- eslint-disable-next-line vue/valid-v-for max-len -->
            <template v-for="(m, index) in r.genes">{{ index == 0 ? '' : ', ' }}<router-link :to="{ path: `/explore/gem-browser/${model.database_name}/gene/${m.id}` }">{{ m.name || m.id }}</router-link>
            </template>
          </td>
          <td v-show="showCP">{{ r.cp }}</td>
          <td v-show="showSubsystem">
            <template v-if="r.subsystem_str">
              <!-- eslint-disable-next-line vue/valid-v-for max-len -->
              <template v-for="(s, index) in r.subsystem_str.split('; ')">{{ index == 0 ? '' : '; ' }}<router-link :to="{ path: `/explore/gem-browser/${model.database_name}/subsystem/${idfy(s)}` }">{{ s }}</router-link>
              </template>
            </template>
          </td>
          <td>
            <template v-for="(RP, i) in r.compartment.split(' => ')">
              <template v-if="i != 0">{{ r.is_reversible ? ' &#8660; ' : ' &#8658; ' }}</template>
              <template v-for="(compo, j) in RP.split(' + ')">
                <template v-if="j != 0"> + </template>
                <!-- eslint-disable-next-line vue/valid-v-for -->
                <router-link
                  :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${idfy(compo)}` }"
                > {{ compo }}</router-link>
              </template>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import $ from 'jquery';
import { default as compare } from '../../../helpers/compare';
import { chemicalReaction } from '../../../helpers/chemical-formatters';
import { reformatCompEqString, idfy, reformatChemicalReactionHTML } from '../../../helpers/utils';

export default {
  name: 'ReactionTable',
  props: {
    model: Object,
    reactions: Array,
    selectedElmId: String,
    limit: Number,
    showSubsystem: Boolean,
  },
  data() {
    return {
      fields: [{
        display: 'Reaction ID',
        name: 'id',
      }, {
        display: 'Equation',
        name: 'equation',
      }, {
        display: 'Genes',
        name: 'genes',
      }, {
        display: 'C/P',
        name: 'cp',
      }, {
        display: 'Subsystem',
        name: 'subsystem_str',
      }, {
        display: 'Compartment',
        name: 'compartment',
      }],
      // sortedReactions: [],
      sortOrder: 'asc',
      sortBy: 'id',
      sortPattern: '',
      reformatCompEqString,
    };
  },
  computed: {
    showCP() {
      return this.selectedElmId; // true or false
    },
    transportReactionCount() {
      return this.reactions.filter(r => r.is_transport).length;
    },
    sortedReactions() {
      /* eslint-disable no-param-reassign */
      if (this.reactions.length === 0) {
        return [];
      }
      // create consume/produce column
      if (this.selectedElmId) {
        this.reactions.forEach((reaction) => {
          if (reaction.is_reversible) {
            reaction.cp = 'consume/produce';
          } else {
            const boolC = reaction.reactionreactant_set.filter(
              e => e.reactant.id === this.selectedElmId);
            if (boolC.length !== 0) {
              reaction.cp = 'consume';
            } else {
              const boolP = reaction.reactionproduct_set.filter(
                e => e.product.id === this.selectedElmId);
              if (boolP.length !== 0) {
                reaction.cp = 'produce';
              }
            }
          }
        });
      }
      return this.reactions.concat().sort(
        compare(this.sortBy, this.sortPattern, this.sortOrder));
    },
  },
  updated() {
    if (this.selectedElmId) {
      // when the table is from the selectedElmId page (metabolite)
      // do not color the selectedElmId is the reaction equations
      $('m').css('color', '');
      $(`.${this.selectedElmId}`).addClass('cms');
    }
  },
  methods: {
    formatChemicalReaction(v, r) { return chemicalReaction(v, r); },
    getReformatChemicalReactionHTML(r) {
      return reformatChemicalReactionHTML(r);
    },
    sortTable(field, pattern, order) {
      if (order) {
        this.sortOrder = order;
      } else if (field !== this.sortBy) {
        this.sortOrder = 'asc';
      } else {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      }
      this.sortBy = field;
      this.sortPattern = pattern;
    },
    showCol(name) {
      if ((name === 'cp' && !this.showCP) || (name === 'subsystem_str' && !this.showSubsystem)) {
        return false;
      }
      return true;
    },
    idfy,
    reformatChemicalReactionHTML,
  },
};

</script>

<style lang="scss">

.reaction-table {

  m {
    color: #00549E;
    &.cms {
      color: rgb(54, 54, 54);
      cursor: default;
      font-weight: 600;
    }
  }
}

</style>
