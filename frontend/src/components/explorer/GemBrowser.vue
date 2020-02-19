<template>
  <div>
    <template v-if="errorMessage">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </template>
    <template v-else>
      <div v-if="!selectedType" class="columns">
        <div class="column container has-text-centered">
          <h3 class="title is-3">Explore {{ model.short_name }} with the {{ messages.gemBrowserName }}</h3>
          <h5 class="subtitle is-5 has-text-weight-normal">
            use the search field to find the component of interest
          </h5>
        </div>
      </div>
      <div class="columns is-centered">
        <gem-search ref="gemSearch" :model="model"></gem-search>
      </div>
      <div v-if="showTiles && !selectedType">
        <div class="columns is-centered">
          <div class="column is-10 is-size-5 has-text-centered">
            <br><br>
            <a id="randomButton" class="button is-rounded is-outlined is-size-5 is-success"
               title="Fetch another random set of components" @click="get_tiles_data()">
              <span class="icon">
                <i class="fa fa-random"></i>
              </span>
              <span>random components of {{ model.short_name }}</span>
            </a>
            <br>
          </div>
        </div>
        <div v-if="tileComponents" id="gem-browser-tiles" class="tile is-ancestor is-size-5">
          <div class="tile">
            <div class="tile is-vertical is-9">
              <div class="tile">
                <tile type="reaction" :model="model" :data="tileComponents.reactions[0]">
                </tile>
                <div class="tile is-vertical is-8">
                  <tile type="subsystem" :model="model" :data="tileComponents.subsystems[0]">
                  </tile>
                  <div class="tile">
                    <tile type="gene" size="is-6"
                          :model="model" :data="tileComponents.genes[0]">
                    </tile>
                    <tile type="metabolite" size="is-6"
                          :model="model" :data="tileComponents.metabolites[0]">
                    </tile>
                  </div>
                </div>
              </div>
              <div class="tile">
                <div class="tile is-vertical is-8">
                  <div class="tile">
                    <tile type="subsystem" :model="model" :data="tileComponents.subsystems[1]">
                    </tile>
                  </div>
                  <div class="tile">
                    <tile type="metabolite" size="is-6"
                          :model="model" :data="tileComponents.metabolites[1]">
                    </tile>
                    <tile type="gene" size="is-6"
                          :model="model" :data="tileComponents.genes[1]">
                    </tile>
                  </div>
                </div>
                <div class="tile is-4">
                  <tile type="reaction" :model="model" :data="tileComponents.reactions[1]">
                  </tile>
                </div>
              </div>
            </div>
            <div class="tile is-vertical">
              <tile type="compartment" :model="model" :data="tileComponents.compartment">
              </tile>
            </div>
          </div>
        </div>
      </div>
      <div v-show="selectedType">
        <keep-alive>
          <gene v-if="selectedType==='gene'" :model="model"></gene>
          <metabolite v-if="selectedType==='metabolite'" :model="model"></metabolite>
          <reaction v-if="selectedType==='reaction'" :model="model"></reaction>
          <subsystem v-if="selectedType==='subsystem'" :model="model"></subsystem>
          <compartment v-if="selectedType==='compartment'" :model="model"></compartment>
        </keep-alive>
      </div>
    </template>
  </div>
</template>

<script>
import axios from 'axios';
import GemSearch from '@/components/explorer/gemBrowser/GemSearch';
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
  name: 'GemBrowser',
  components: {
    Gene,
    Metabolite,
    Reaction,
    Subsystem,
    Compartment,
    GemSearch,
    Tile,
  },
  props: {
    model: Object,
  },
  data() {
    return {
      messages,
      selectedType: '',

      showTiles: true,
      errorMessage: '',
      tileComponents: null,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.selectedType = '';
      this.setup();
    },
  },
  beforeMount() {
    this.setup();
  },
  created() {
    // init the global events
    EventBus.$off('GBnavigateTo');
    EventBus.$on('GBnavigateTo', (type, id) => {
      let ID = id;
      if (type === 'subsystem' || type === 'compartment') {
        ID = idfy(id);
      }
      this.$router.push({ name: 'browser', params: { model: this.model.database_name, type, id: ID } });
    });
  },
  methods: {
    setup() {
      if (['browser', 'browserRoot'].includes(this.$route.name)) {
        if (!this.model || this.model.database_name !== this.$route.params.model) {
          EventBus.$emit('modelSelected', '');
          this.errorMessage = `Error: ${messages.modelNotFound}`;
          return;
        }
        if (this.$route.name === 'browserRoot') {
          this.get_tiles_data();
        } else if (this.selectedType === 'interaction') {
          this.$router.replace(`/explore/interaction/${this.model.database_name}/${this.componentID}`);
        } else {
          this.selectedType = this.$route.params.type;
        }
        this.showTiles = this.tileComponents !== null;
      }
    },
    get_tiles_data() {
      axios.get(`${this.model.database_name}/gem_browser_tiles/`)
        .then((response) => {
          this.tileComponents = response.data;
          this.showTiles = true;
        })
        .catch(() => {
          this.errorMessage = messages.unknownError;
          this.showTiles = false;
        });
    },
  },
};

</script>

<style lang="scss">

#gem-browser-tiles {
  word-wrap: anywhere;
  .tile.is-child {
    ul {
      list-style-type: disc;
      margin-left: 2rem;
    }
  }
}

#randomButton {
  vertical-align: inherit;
}

</style>
