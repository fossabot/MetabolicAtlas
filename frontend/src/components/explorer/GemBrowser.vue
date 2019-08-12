<template>
  <div>
    <template v-if="errorMessage">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </template>
    <template v-else>
      <div class="columns" v-if="!selectedType">
        <div class="column container has-text-centered">
          <h4 class="title is-4">Explore {{ model.short_name }} with the {{ messages.gemBrowserName }}</h4>
        </div>
      </div>
      <div class="columns is-centered">
        <gem-search :model="model" ref="gemSearch"></gem-search>
      </div>
      <div v-if="selectedType === ''">
        <div class="columns is-centered">
          <div class="column is-10 is-size-5 has-text-centered">
            Use the search field above to look for your constituent of interest.<br>
            A selection of <b>random</b> constituents of {{ model.short_name }} is shown below.<br><br>
          </div>
        </div>
        <div id="gem-browser-tiles" class="tile is-ancestor is-size-5" v-if="starredComponents">
            <div class="tile">
              <div class="tile is-vertical is-9">
                <div class="tile">
                  <tile type="reaction" :model="model" :data="starredComponents.reactions[0]">
                  </tile>
                  <div class="tile is-vertical is-8">
                    <tile type="subsystem" :model="model" :data="starredComponents.subsystems[0]">
                    </tile>
                    <div class="tile">
                      <tile type="gene" size="is-6" :model="model" :data="starredComponents.genes[0]">
                      </tile>
                      <tile type="metabolite" size="is-6" :model="model" :data="starredComponents.metabolites[0]">
                      </tile>
                    </div>
                  </div>
                </div>
                <div class="tile">
                  <div class="tile is-vertical is-8">
                    <div class="tile">
                      <tile type="subsystem" :model="model" :data="starredComponents.subsystems[1]">
                      </tile>
                    </div>
                    <div class="tile">
                      <tile type="metabolite" size="is-6" :model="model" :data="starredComponents.metabolites[1]">
                      </tile>
                      <tile type="gene" size="is-6" :model="model" :data="starredComponents.genes[1]">
                      </tile>
                    </div>
                  </div>
                  <div class="tile is-4">
                    <tile type="reaction" :model="model" :data="starredComponents.reactions[1]">
                    </tile>
                  </div>
                </div>
              </div>
              <div class="tile is-vertical">
                <tile type="compartment" :model="model" :data="starredComponents.compartment">
                </tile>
              </div>
            </div>
        </div>
      </div>
      <div v-else>
        <closest-interaction-partners v-if="selectedType==='interaction'" :model="model"></closest-interaction-partners>
        <gene v-if="selectedType==='gene'" :model="model"></gene>
        <metabolite v-if="selectedType==='metabolite'" :model="model"></metabolite>
        <reaction v-if="selectedType==='reaction'" :model="model"></reaction>
        <subsystem v-if="selectedType==='subsystem'" :model="model"></subsystem>
        <compartment v-if="selectedType==='compartment'" :model="model"></compartment>
      </div>
    </template>
  </div>
</template>

<script>
import Vue from 'vue';
import axios from 'axios';
import GemSearch from '@/components/explorer/gemBrowser/GemSearch';
import ClosestInteractionPartners from '@/components/explorer/gemBrowser/ClosestInteractionPartners';
import Gene from '@/components/explorer/gemBrowser/Gene';
import Metabolite from '@/components/explorer/gemBrowser/Metabolite';
import Reaction from '@/components/explorer/gemBrowser/Reaction';
import Subsystem from '@/components/explorer/gemBrowser/Subsystem';
import Compartment from '@/components/explorer/gemBrowser/Compartment';
import Tile from '@/components/explorer/gemBrowser/Tile';
import { default as messages } from '../../helpers/messages';
import { default as EventBus } from '../../event-bus';
import { idfy } from '../../helpers/utils';


export default {
  name: 'gem-browser',
  props: ['model'],
  components: {
    ClosestInteractionPartners,
    Gene,
    Metabolite,
    Reaction,
    Subsystem,
    Compartment,
    GemSearch,
    Tile,
  },
  data() {
    return {
      messages,
      selectedType: '',
      searchTerm: '',
      searchResults: [],
      errorMessage: '',
      componentID: '',
      mapsAvailable: null,
      starredComponents: null,
      newStarredComponents: null,
      interval: null,
      timeoutLoop: null,
      timeout: 4000, // initial value
      maxTileUpdateCount: 90, // 1 hour
      counter: 0
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  beforeMount() {
    this.setup();
  },
  created() {
    // init the global events
    EventBus.$off('resetView');
    EventBus.$off('GBnavigateTo');
    EventBus.$off('viewReactionOnMap');

    EventBus.$on('resetView', () => {
      this.levelSelected = 'subsystem';
      EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
    });
    EventBus.$on('GBnavigateTo', (type, id) => {
      let ID = id;
      if (type === 'subsystem' || type === 'compartment') {
        ID = idfy(id);
      }
      this.$router.push(`/explore/gem-browser/${this.$route.params.model}/${type}/${ID}`);
    });
  },
  mounted() {
    this.$nextTick(function () {
      this.loop();
    });
  },
  methods: {
    setup() {
      if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        if (!this.model || this.model.database_name !== this.$route.params.model) {
          EventBus.$emit('modelSelected', '');
          this.errorMessage = `Error: ${messages.modelNotFound}`;
          return;
        }
        this.selectedType = this.$route.params.type || '';
        this.componentID = this.$route.params.id || '';
        if (!this.componentID || !this.selectedType) {
          this.$router.push(`/explore/gem-browser/${this.model.database_name}`);
          if (!this.starredComponents) {
            this.get_tiles_data();
          }
        }
      }
    },
    get_tiles_data() {
      axios.get(`${this.model.database_name}/gem_browser_tiles/`)
      .then((response) => {
        for (const k of Object.keys(response.data)) {
          if (Array.isArray(response.data[k])) {
            response.data[k][0].hidden = false; response.data[k][1].hidden = false;
          } else {
            response.data[k].hidden = false;
          }
        }
        this.starredComponents = response.data;
      })
      .catch(() => {
        this.errorMessage = messages.unknownError;
      });
    },
    loop() {
      this.update_starred_components();
      this.timeoutLoop = window.setTimeout(this.loop, this.timeout);
      if (this.timeout !== 40000) {
        this.timeout = 40000;
      }
      if (this.counter === this.maxTileUpdateCount) {
        clearTimeout(this.timeoutLoop);
      }
      this.counter += 1;
    },
    update_starred_components() {
      if (this.selectedType !== '' || this._inactive) {
        // do not update tiles when the GB is not on the screen or when the tiles are not shown
        if (this.interval) {
          clearInterval(this.interval);
        }
        return;
      }
      axios.get(`${this.model.database_name}/gem_browser_tiles/`)
      .then((response) => {
        if (this.interval) {
          clearInterval(this.interval);
        }
        this.newStarredComponents = response.data;
        // add the 'hidden' key
        for (const v of Object.values(this.newStarredComponents)) {
           if (Array.isArray(v)) {
            v[0].hidden = false; v[1].hidden = false;
           } else {
            v.hidden = false;
           }
        }
        this.interval = setInterval(() => {
          if (Object.keys(this.newStarredComponents).length === 0) {
            return;
          }
          const index = Math.floor(Math.random() * Math.floor(Object.keys(this.newStarredComponents).length));
          const key = Object.keys(this.newStarredComponents)[index];
          if (Array.isArray(this.newStarredComponents[key])) {
            this.update_tiles_data(key);
          } else {
            this.starredComponents[key].hidden = true;
            setTimeout(() => {
              this.newStarredComponents[key].hidden = false;
              Vue.set(this.starredComponents, key, JSON.parse(JSON.stringify(this.newStarredComponents[key])));
              delete this.newStarredComponents[key];
            },500);
          }
        }, 4000);
      })
      .catch(() => {
        this.errorMessage = messages.unknownError;
      });
    },
    update_tiles_data(key) {
      // select a random index of the array (reaction / gene/ metabolite / subsystem)
      let indexArr = Math.floor(Math.random() * Math.floor(this.newStarredComponents[key].length));
      if (!this.newStarredComponents[key][indexArr]) {
        indexArr ^= 1;
      }
      this.starredComponents[key][indexArr].hidden = true;
      setTimeout(() => {
        if (indexArr === 0) {
          this.starredComponents[key] = [JSON.parse(JSON.stringify(this.newStarredComponents[key][indexArr])), this.starredComponents[key][1]];
          this.newStarredComponents[key][indexArr] = '';
        } else {
          this.starredComponents[key] = [this.starredComponents[key][0], JSON.parse(JSON.stringify(this.newStarredComponents[key][indexArr]))];
          this.newStarredComponents[key][indexArr] = '';
        }
        if (this.newStarredComponents[key].filter(e => e).length === 0) {
          delete this.newStarredComponents[key];
        }
      },500);
    },
    showMapViewer() {
      EventBus.$emit('showMapViewer');
    },
  },
};

</script>

<style lang="scss">
</style>
