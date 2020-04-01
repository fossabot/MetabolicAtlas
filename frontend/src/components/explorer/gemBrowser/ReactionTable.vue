<template>
  <div class="reaction-table">
    <div class="field">
      <span class="tag is-medium" :class="reactions.length === limit ? 'is-warning' : ''">
        # Reactions: {{ reactions.length }}
      </span>
      <template v-if="transportReactionCount !== 0">
        &nbsp;including&nbsp;
        <span class="tag is-medium clickable" @click="sortTable('is_transport', null, 'desc')">
          {{ transportReactionCount }} transport reactions
        </span>
      </template>
      <ExportTSV
        class="is-pulled-right"
        :style="{ 'margin-left': '1rem' }"
        :filename="`reaction_${sourceName}.tsv`"
        :format-function="formatToTSV"
      ></ExportTSV>
      <span v-show="reactions.length === limit" class="tag is-medium is-warning is-pulled-right">
        The number of reactions displayed is limited to {{ limit }}.
      </span>
    </div>
    <div class="table-container">
      <table ref="table" class="table is-bordered is-striped is-narrow is-fullwidth">
        <thead>
          <tr class="has-background-white-ter">
            <th v-for="f in fields" v-show="showCol(f.name)"
                :key="f.name" class="is-unselectable clickable"
                :title="`Sort by ${f.display}`"
                @click="sortTable(f.name, null, null)">
              {{ f.display.replace(' ', '&nbsp;') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in sortedReactions" :key="r.id">
            <td>
              <a
                :href="`/explore/gem-browser/${model.database_name}/reaction/${r.id}`"
                @click="handleRouterClick">
                {{ r.id }}
              </a>
            </td>
            <td v-html="reformatChemicalReactionHTML(r, false, model.database_name, selectedElmId)"></td>
            <td>
              <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
              <template v-for="(m, index) in r.genes">{{ index == 0 ? '' : ', ' }}<a :class="{'cms' : sourceName === m.name }" :href="`/explore/gem-browser/${model.database_name}/gene/${m.id}`" @click="handleRouterClick">{{ m.name || m.id }}</a>
              </template>
            </td>
            <td v-show="showCP">{{ r.cp }}</td>
            <td v-show="showSubsystem">
              <template v-if="r.subsystem_str">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                <template v-for="(s, index) in r.subsystem_str.split('; ')">{{ index == 0 ? '' : '; ' }}<a :href="`/explore/gem-browser/${model.database_name}/subsystem/${idfy(s)}`" @click="handleRouterClick">{{ s }}</a>
                </template>
              </template>
            </td>
            <td>
              <template v-for="(RP, i) in r.compartment_str.split(' => ')">
                <template v-if="i !== 0">{{ r.is_reversible ? ' &#8660; ' : ' &#8658; ' }}</template>
                <template v-for="(compo, j) in RP.split(' + ')">
                  <template v-if="j != 0"> + </template>
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                  <a :href="`/explore/gem-browser/${model.database_name}/compartment/${idfy(compo)}`" @click="handleRouterClick">{{ compo }}</a>
                </template>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { default as compare } from '@/helpers/compare';
import ExportTSV from '@/components/explorer/gemBrowser/ExportTSV';
import { idfy, reformatChemicalReactionHTML, getChemicalReaction } from '@/helpers/utils';

export default {
  name: 'ReactionTable',
  components: {
    ExportTSV,
  },
  props: {
    sourceName: String,
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
        name: 'compartment_str',
      }],
      // sortedReactions: [],
      sortOrder: 'asc',
      sortBy: 'id',
      sortPattern: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
    showCP() {
      return this.selectedElmId; // true or false
    },
    transportReactionCount() {
      return this.reactions.filter(r => r.is_transport).length;
    },
    sortedReactions() {
      let reactionsCopy = [...this.reactions];

      if (reactionsCopy.length === 0) {
        return [];
      }

      // create consume/produce column
      if (this.selectedElmId) {
        reactionsCopy = reactionsCopy.map((r) => {
          const rCopy = { ...r };

          if (rCopy.is_reversible) {
            rCopy.cp = 'consume/produce';
          } else {
            const boolC = rCopy.reactionreactant_set.filter(
              e => e.id === this.selectedElmId);
            if (boolC.length !== 0) {
              rCopy.cp = 'consume';
            } else {
              const boolP = rCopy.reactionproduct_set.filter(
                e => e.id === this.selectedElmId);
              if (boolP.length !== 0) {
                rCopy.cp = 'produce';
              }
            }
          }

          return rCopy;
        });
      }
      return reactionsCopy.concat().sort(
        compare(this.sortBy, this.sortPattern, this.sortOrder));
    },
  },
  methods: {
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
    formatToTSV() {
      let tsvContent = `${this.fields.filter((e) => {
        if ((e.name === 'cp' && !this.showCP)
          || (e.name === 'subsystem_str' && !this.showSubsystem)) {
          return false;
        }
        return true;
      }).map(e => e.display).join('\t')}\n`;
      tsvContent += this.sortedReactions.map((r) => {
        const arr = [];
        arr.push(r.id);
        arr.push(getChemicalReaction(r));
        arr.push(r.genes.map(g => g.name || g.id).join('; '));
        if (this.showCP) {
          arr.push(r.cp);
        }
        if (this.showSubsystem) {
          arr.push(r.subsystem_str);
        }
        arr.push(r.compartment_str);
        return arr.join('\t');
      }).join('\n');
      return tsvContent;
    },
    idfy,
    reformatChemicalReactionHTML,
  },
};

</script>

<style lang="scss">

.reaction-table {
  a.cms {
    color: rgb(54, 54, 54);
    cursor: default;
    font-weight: 600;
  }
}

</style>
