<template>
  <div class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
    <div class="control">
      <div id="input-wrapper">
        <p class="control has-icons-right has-icons-left">
          <!-- eslint-disable max-len -->
          <input id="search" ref="searchInput"
                 v-model="searchTermString" v-debounce:700="searchDebounce" data-hj-whitelist
                 type="text" class="input is-medium"
                 :placeholder="placeholder"
                 @keyup.esc="showResults = false"
                 @focus="showResults = true"
                 @blur="blur()">
          <span v-show="showSearchCharAlert" class="has-text-info icon is-right" style="width: 270px">
            Type at least 2 characters
          </span>
          <span class="icon is-medium is-left">
            <i class="fa fa-search"></i>
          </span>
          <span class="icon is-small is-right">
            <i class="fa" :class="metabolitesAndGenesOnly ? 'fa-share-alt' : 'fa-table'"></i>
          </span>
        </p>
        <router-link class="is-pulled-right is-size-5" :to="{ name: 'search', query: { term: searchTermString } }">
          Global search
        </router-link>
      </div>
      <div v-show="showResults && searchTermString.length > 1" id="searchResults" ref="searchResults">
        <div v-show="searchResults.length !== 0 && !showLoader" id="asn"
             class="notification is-large is-unselectable has-text-centered clickable"
             @mousedown.prevent="globalSearch">
          Limited to 50 results per type. Click to search all integrated GEMs
        </div>
        <div v-show="!showLoader" v-if="searchResults.length !== 0" class="resList">
          <template v-for="k in resultsOrder">
            <div v-for="(r, i2) in searchResults[k]" :key="`${r.id}-${i2}`" class="searchResultSection">
              <hr v-if="i2 !== 0" class="is-marginless">
              <router-link class="clickable" :to="getRouterUrl(k, r.id || r.name)"
                           @click.native="showResults=false">
                <b class="is-capitalized">{{ k }}: </b>
                <label class="clickable" v-html="formatSearchResultLabel(k, r, searchTermString)"></label>
              </router-link>
            </div>
            <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
            <hr v-if="searchResults[k].length !== 0" class="bhr">
          </template>
        </div>
        <div v-show="showLoader" class="has-text-centered">
          <a class="button is-primary is-inverted is-outlined is-large is-loading"></a>
        </div>
        <div v-show="!showLoader && noResult" class="has-text-centered notification is-marginless">
          {{ messages.searchNoResult }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import { sortResults, idfy } from '../../../helpers/utils';
import { chemicalFormula, chemicalReaction } from '../../../helpers/chemical-formatters';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'GemSearch',
  props: {
    searchTerm: String,
    model: Object,
    metabolitesAndGenesOnly: Boolean,
  },
  data() {
    return {
      errorMessage: '',
      resultsOrder: ['metabolite', 'gene', 'reaction', 'subsystem', 'compartment'],
      searchResults: [],
      searchTermString: '',
      showSearchCharAlert: false,
      showResults: true,
      showLoader: false,
      noResult: false,
      messages,
      itemKeys: {
        gene: ['id', 'name'],
        reaction: ['id', 'equation'],
        metabolite: ['id', 'name', 'compartment'],
        subsystem: ['name', 'system'],
        compartment: ['name'],
      },
    };
  },
  computed: {
    placeholder() {
      if (this.metabolitesAndGenesOnly) {
        return 'uracil, malate, SULT1A3, CNDP1';
      }
      return 'uracil, SULT1A3, ATP => cAMP + PPi, subsystem or compartment';
    },
  },
  mounted() {
    $('#search').focus();
  },
  methods: {
    blur() {
      setTimeout(() => { this.showResults = false; }, 200);
    },
    searchDebounce() {
      this.noResult = false;
      this.showSearchCharAlert = this.searchTermString.length === 1;
      this.showLoader = true;
      if (this.searchTermString.length > 1) {
        this.showResults = true;
        this.search(this.searchTermString);
      }
    },
    search(searchTerm) {
      this.searchTermString = searchTerm;
      const url = `${this.model.database_name}/search/${searchTerm}`;
      axios.get(url)
        .then((response) => {
          const localResults = {
            metabolite: [],
            gene: [],
            reaction: [],
            subsystem: [],
            compartment: [],
          };

          Object.keys(response.data).forEach((model) => {
            const resultsModel = response.data[model];
            this.resultsOrder.forEach((resultType) => {
              if (this.metabolitesAndGenesOnly && !['metabolite', 'gene'].includes(resultType)) {
                return;
              }
              if (resultsModel[resultType]) {
                localResults[resultType] = localResults[resultType].concat(
                  resultsModel[resultType].map(
                    (e) => {
                      const d = e; d.model = { id: model, name: resultsModel.name }; return d;
                    })
                );
              }
            });
          });
          this.searchResults = localResults;

          this.noResult = true;
          const keyList = Object.keys(this.searchResults);
          for (let i = 0; i < keyList.length; i += 1) {
            const k = keyList[i];
            if (this.searchResults[k].length) {
              this.showSearchCharAlert = false;
              this.noResult = false;
              break;
            }
          }
          this.showLoader = false;
          // sort result by exact matched first, then by alpha order
          Object.keys(localResults).forEach((k) => {
            if (localResults[k].length) {
              localResults[k].sort((a, b) => this.sortResults(a, b, this.searchTermString));
            }
          });
          this.$refs.searchResults.scrollTop = 0;
        })
        .catch(() => {
          this.searchResults = [];
          this.noResult = true;
          this.showLoader = false;
        });
    },
    getRouterUrl(type, id) {
      let ID = id;
      if (type === 'subsystem' || type === 'compartment') {
        ID = idfy(id);
      }
      if (this.metabolitesAndGenesOnly) {
        return `/explore/interaction/${this.$route.params.model}/${ID}`;
      }
      return `/explore/gem-browser/${this.$route.params.model}/${type}/${ID}`;
    },
    globalSearch() {
      this.$router.push({ name: 'search', query: { term: this.searchTermString } });
    },
    formatSearchResultLabel(type, element, searchTerm) {
      const re = new RegExp(`(${searchTerm})`, 'ig');
      let s = '';
      this.itemKeys[type].filter(key => element[key]).forEach((key) => {
        if (key === 'equation') {
          s = `${s} ‒ ${chemicalReaction(element[key].replace(re, '<b>$1</b>'), element.is_reversible)}`;
        } else {
          // do not HL the compartment name
          s = key === 'compartment_str' ? `${s} ‒ ${element[key]}` : `${s} ‒ ${element[key].replace(re, '<b>$1</b>')}`;
        }
      });
      if (s.length !== 0) {
        return s.slice(2);
      }
      return s;
    },
    chemicalFormula,
    sortResults,
  },
};
</script>

<style lang="scss">

#input-wrapper {
  position: relative; /* for absolute child element */
}

#searchResults {
  background: white;
  position: absolute;
  top: 37px;
  overflow-x: hidden;
  width: 100%;
  border: 1px solid lightgray;
  border-top: 0;
  margin-top: -2px;
  z-index: 30;

  #asn {
    padding: 4px;
  }

  .resList {
      max-height: 22rem;
      overflow-y: auto;
  }

  hr {
    &.bhr {
      margin: 5px 7px;
      padding: 0;
      border-top: 3px double #000000;
    }
  }
  .bhr:last-child {
    display: none;
  }

  .searchResultSection {
    padding: 0px 10px;
    a {
      display:block;
      padding: 7px 0px;
    }
  }
}

</style>
