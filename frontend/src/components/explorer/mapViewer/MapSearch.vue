<template>
  <div id="svgSearch" class="overlay" :class="[{'fullscreen' : fullscreen}]">
    <div class="control" :class="{ 'is-loading' : isSearching }">
      <input id="searchInput" v-model.trim="searchTerm" data-hj-whitelist
             title="Exact search by id, name, alias. Press Enter for results" class="input"
             type="text" :class="searchInputClass"
             :disabled="!ready" placeholder="Exact search by id, name, alias"
             @keyup.enter="search()" />
    </div>
    <template v-if="searchTerm && matches && matches.length !== 0 && totalSearchMatch !== 0">
      <span id="searchResCount" class="button has-text-dark"
            title="Click to center on current match"
            @click="centerViewOn(0)">
        {{ currentSearchMatch + 1 }} of {{ totalSearchMatch }}
      </span>
      <span class="button has-text-dark"
            title="Go to previous"
            @click="centerViewOn(-1)"><i class="fa fa-angle-left"></i></span>
      <span class="button has-text-dark"
            title="Go to next"
            @click="centerViewOn(1)"><i class="fa fa-angle-right"></i></span>
      <span class="button has-text-dark"
            title="Highlight all matches"
            @click="highlightAll()">Highlight all</span>
    </template>
    <template v-else-if="searchTerm && totalSearchMatch === 0 && haveSearched">
      <span class="has-text-white">{{ messages.searchNoResult }}</span>
    </template>
  </div>
</template>

<script>

import axios from 'axios';
// import { default as EventBus } from '../../../event-bus';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'MapSearch',
  props: {
    model: Object,
    matches: Array, // list of match objects on the map/network
    ready: Boolean,
    fullscreen: Boolean,
  },
  data() {
    return {
      errorMessage: '',
      idsFound: [],

      searchTerm: '',
      searchInputClass: '',
      isSearching: false,

      currentSearchMatch: 0,
      totalSearchMatch: 0,
      haveSearched: false,
      messages,
    };
  },
  watch: {
    searchTerm() {
      if (!this.searchTerm) {
        this.unHighlightAll();
        this.totalSearchMatch = 0;
        this.currentSearchMatch = 0;
        this.searchInputClass = 'is-info';
      }
      this.haveSearched = false;
    },
    matches() {
      console.log('this.matches', this.matches);
      if (this.matches === null) {
        // reset
        this.searchTerm = '';
        this.totalSearchMatch = 0;
        this.currentSearchMatch = 0;
        this.searchInputClass = 'is-info';
      } else {
        console.log('hereeeee');
        this.isSearching = false;
        if (this.matches.length === 0) {
          this.searchInputClass = 'is-danger';
        } else {
          this.searchInputClass = 'is-success';
        }
        this.currentSearchMatch = 0;
        this.totalSearchMatch = this.matches.length;
        this.haveSearched = false;
      }
    },
  },
  created() {
  },
  mounted() {
  },
  methods: {
    search() {
      this.idsFound = [];
      if (!this.searchTerm) {
        this.searchInputClass = 'is-warning';
        return;
      }
      // get the IDs from the backend, then search in the SVG
      // this.unHighlight();
      this.isSearching = true;
      console.log('search term', this.searchTerm);
      axios.get(`${this.model.database_name}/get_id/${this.searchTerm}`)
        .then((response) => {
          // results are on the model, but may not be on the displayed map/network!
          this.idsFound = response.data;
          this.totalSearchMatch = 0;
          this.currentSearchMatch = 0;
        })
        .catch((err) => {
          console.log(err);
          this.searchInputClass = 'is-danger';
        })
        .then(() => {
          this.isSearching = false;
          this.haveSearched = true;
          console.log('emit idsFound', this.idsFound);
          this.$emit('searchOnMap', this.idsFound); // let the view call its own search function
        });
    },
    centerViewOn(position) {
      if (this.matches.length === 0) {
        return;
      }
      this.currentSearchMatch += position;
      if (this.currentSearchMatch < 0) {
        this.currentSearchMatch = this.totalSearchMatch - 1;
      } else if (this.currentSearchMatch > this.totalSearchMatch - 1) {
        this.currentSearchMatch = 0;
      }
      this.$emit('centerViewOn', this.matches[this.currentSearchMatch]);
    },
    highlightAll() {
      this.$emit('highlightAll', this.matches);
    },
    unHighlightAll() {
      this.$emit('unHighlightAll', this.matches);
    },
    setSearchTerm(term) {
      this.searchTerm = term;
    },
  },
};
</script>

<style lang="scss">
  #svgSearch {
    top: 2.25rem;
    left: 30%;
    margin: 0;
    padding: 15px;
    div {
      display: inline-block;
      vertical-align: middle;
    }
    span {
      margin-left: 5px;
    }
    #searchInput {
      display: inline-block;
      width: 20vw;
    }
    &.fullscreen {
      left: 30%;
      #searchInput {
        width: 30vw;
      }
    }
  }
</style>
