<template>
  <div class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
    <div class="control">
      <div>
        <p class="control has-icons-right has-icons-left">
          <!-- eslint-disable max-len -->
          <input id="search" ref="searchInput"
                 v-debounce:700="searchDebounce" data-hj-whitelist
                 type="text" class="input"
                 :placeholder="placeholder"
                 :value="searchTermString"
                 @keyup.esc="showResults = false"
                 @focus="showResults = true"
                 @blur="blur()">
          <span v-show="showSearchCharAlert" class="has-text-info icon is-right" style="width: 270px">
            Type at least 2 characters
          </span>
          <span class="icon is-medium is-left">
            <i class="fa" :class="metabolitesAndGenesOnly ? 'fa-connectdevelop' : 'fa-table'"></i>
          </span>
        </p>
        <router-link v-if="$route.name === 'browser'"
                     class="is-pulled-left has-text-grey-light"
                     :to="{ name: 'browserRoot', params: { model: model.database_name } }">
          &larr; back to tiles
        </router-link>
        <router-link class="is-pulled-right" :to="{ name: 'search', query: { term: searchTermString } }">
          Global Search
        </router-link>
      </div>
      <div v-show="showResults && searchTermString.length > 1" id="searchResults" ref="searchResults">
        <div v-show="searchResults.length !== 0 && !showLoader" id="asn"
             class="notification is-large is-unselectable has-text-centered clickable"
             @mousedown.prevent="globalSearch">
          Limited to 50 results per type. Click to search all integrated GEMs
        </div>
        <div v-show="!showLoader" v-if="searchResults.length !== 0" class="resList">
          <template v-for="type in resultsOrder">
            <div v-for="(r, i2) in searchResults[type]" :key="`${r.id}-${i2}`" class="searchResultSection">
              <hr v-if="i2 !== 0" class="is-marginless">
              <router-link class="clickable" :to="getRouterUrl(type, r.id)"
                           @click.native="showResults=false">
                <b class="is-capitalized">{{ type }}: </b>
                <label class="clickable" v-html="formatSearchResultLabel(type, r, searchTermString)"></label>
              </router-link>
            </div>
            <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
            <hr v-if="searchResults[type] && searchResults[type].length !== 0" class="bhr">
          </template>
        </div>
        <div v-show="showLoader" class="has-text-centered">
          <a class="button is-primary is-inverted is-outlined is-large is-loading"></a>
        </div>
        <div v-show="!showLoader && noResult" class="has-text-centered notification is-marginless">
          {{ messages.searchNoResult }}
          <div v-if="notFoundSuggestions.length !== 0">
            Do you mean:&nbsp;
            <template v-for="v in notFoundSuggestions">
              <a :key="v" class="suggestions has-text-link" @click.prevent="searchDebounce(v)">{{ v }}</a>&nbsp;
            </template>?
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import $ from 'jquery';
import { chemicalReaction } from '@/helpers/chemical-formatters';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'GemSearch',
  props: {
    searchTerm: String,
    metabolitesAndGenesOnly: Boolean,
  },
  data() {
    return {
      errorMessage: '',
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
      notFoundSuggestions: [],
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      resultsOrder: state => state.search.categories,
      searchTermString: state => state.search.searchTermString,
    }),
    ...mapGetters({
      searchResults: 'search/categorizedAndSortedResults',
    }),
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
      setTimeout(() => { this.showResults = $('#search').is(':focus'); }, 200);
    },
    async searchDebounce(searchTerm) {
      this.noResult = false;
      this.showSearchCharAlert = searchTerm.length === 1;
      this.$store.dispatch('search/setSearchTermString', searchTerm);

      const canSearch = searchTerm.length > 1;

      this.showLoader = canSearch;
      this.showResults = canSearch;
      if (canSearch) {
        await this.search(searchTerm);
      }
    },
    async search() {
      $('#search').focus();
      if (this.searchTermString.length < 2) {
        return;
      }

      try {
        const payload = {
          model: this.model.database_name,
          metabolitesAndGenesOnly: this.metabolitesAndGenesOnly,
        };
        await this.$store.dispatch('search/search', payload);

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
        this.$refs.searchResults.scrollTop = 0;
      } catch (error) {
        this.$store.dispatch('search/clearSearchResults');
        this.noResult = true;
        if (error.response.headers.suggestions) {
          this.notFoundSuggestions = JSON.parse(error.response.headers.suggestions);
        } else {
          this.notFoundSuggestions = [];
        }
        this.showLoader = false;
      }
    },
    getRouterUrl(type, id) {
      if (this.metabolitesAndGenesOnly) {
        return `/explore/interaction/${this.$route.params.model}/${id}`;
      }
      return `/explore/gem-browser/${this.$route.params.model}/${type}/${id}`;
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
  },
};
</script>

<style lang="scss">

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
