<template>
  <div id="sidebar_mapviewer">
    <div v-if="mapName" class="card card-margin">
      <header class="card-header" @click.prevent="showMapCardContent = !showMapCardContent">
        <p class="card-header-title is-capitalized is-inline">
          {{ mapType }}:
          <i>{{ mapsData.compartments[mapName] ?
            mapsData.compartments[mapName].name : mapsData.subsystems[mapName] ?
              mapsData.subsystems[mapName].name : '' }}</i>
        </p>
      </header>
      <footer class="card-footer">
        <router-link class="is-paddingless is-info is-outlined card-footer-item has-text-centered"
                     :to="{ name: 'browser', params: { model: model.database_name, type: mapType, id: getGemBrowserLinkId() } }">  <!-- eslint-disable-line max-len -->
          <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
          <span>{{ messages.gemBrowserName }}</span>
        </router-link>
      </footer>
    </div>
    <template v-if="loading">
      <div class="loading">
        <a class="button is-large is-loading"></a>
      </div>
    </template>
    <template v-else-if="!selectionData.error">
      <div v-if="selectionData.data && mapType !== 'subsystem' && selectionData.type === 'subsystem'"
           class="card card-margin">
        <header class="card-header">
          <p class="card-header-title is-capitalized is-inline is-unselectable">
            {{ selectionData.type }}: <i>{{ selectionData.data.id }}</i>
          </p>
        </header>
        <footer class="card-footer">
          <router-link class="is-paddingless is-info is-outlined card-footer-item has-text-centered"
                       :to="{ name: 'browser', params: { model: model.database_name, type: selectionData.type, id: idfy(selectionData.data.id) } }">  <!-- eslint-disable-line max-len -->
            <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
            <span>{{ messages.gemBrowserName }}</span>
          </router-link>
          <template v-if="isAvailableSubsystemMap(selectionData.data.id)">
            <router-link
              class="is-paddingless is-primary is-outlined card-footer-item has-text-centered"
              :to="{ name: 'viewer', params: { model: model.database_name, type: selectionData.type, map_id: idfy(selectionData.data.id) }, query: { dim: '2d' } }">  <!-- eslint-disable-line max-len -->
              <span class="icon is-large"><i class="fa fa-map-o fa-lg"></i></span>
              <span>Load map</span>
            </router-link>
          </template>
          <template v-else>
            <div class="is-paddingless is-primary is-outlined card-footer-item has-text-centered" disabled
                 title="Subsystem map not available">
              <span class="icon is-large"><i class="fa fa-map-o fa-lg"></i></span>
              <span :style="{ cursor: 'not-allowed' }">Load map</span>
            </div>
          </template>
        </footer>
      </div>
      <div v-else-if="selectionData.data && ['metabolite', 'gene', 'reaction'].includes(selectionData.type)"
           class="card card-margin">
        <header class="card-header clickable"
                @click.prevent="showSelectionCardContent = !showSelectionCardContent">
          <p class="card-header-title is-inline is-capitalized is-unselectable">
            {{ selectionData.type }}: <i>{{ selectionData.data.id }}</i>
          </p>
          <a href="#" class="card-header-icon" aria-label="more options">
            <span class="icon">
              <i aria-hidden="true" :class="[showSelectionCardContent ? 'fa-caret-down' : 'fa-caret-right', 'fa']"></i>
            </span>
          </a>
        </header>
        <div v-show="showSelectionCardContent" class="card-content card-content-compact">
          <div class="content">
            <template v-for="item in selectedElementDataKeys[selectionData.type]
              .filter(i => selectionData.data[i.name] !== null)">
              <template v-if="item.name === 'synonyms'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span><p>
                  <template v-for="s in selectionData.data[item.name].split('; ')">
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    &ndash;&nbsp;{{ s }}<br :key="s">
                  </template></p>
              </template>
              <template v-else-if="item.name === 'subsystem'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span><p>
                  <template v-for="s in selectionData.data[item.name]">
                    &ndash;&nbsp;{{ s.name }}<br :key="s.id">
                  </template></p>
              </template>
              <template v-else-if="item.name === 'compartment'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span>
                {{ selectionData.data[item.name].name }}
              </template>
              <template v-else-if="['reactionreactant_set', 'reactionproduct_set'].includes(item.name)">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span>
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p>
                  <template v-for="s in selectionData.data[item.name]">
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    &ndash;&nbsp;{{ s.full_name }}<br>
                  </template>
                </p>
              </template>
              <template v-else-if="item.name === 'equation'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"></span><br>
                  <span v-html="chemicalReaction(selectionData.data[item.name], selectionData.data['is_reversible'])">
                  </span></p>
              </template>
              <template v-else-if="item.name === 'formula'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ': '"></span>
                  <span v-html="chemicalFormula(selectionData.data[item.name], selectionData.data.charge)"></span></p>
              </template>
              <template v-else-if="selectionData.data[item.name]">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"></span>
                  {{ selectionData.data[item.name] }}</p>
              </template>
            </template>
            <template v-if="selectionHasNoData()">
              {{ messages.noInfoAvailable }}
            </template>
          </div>
        </div>
        <footer class="card-footer">
          <router-link class="is-paddingless is-info is-outlined card-footer-item has-text-centered"
                       :to="{ name: 'browser', params: { model: model.database_name, type: selectionData.type, id: idfy(selectionData.data.id) } }"> <!-- eslint-disable-line max-len -->
            <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
            <span>{{ messages.gemBrowserName }}</span>
          </router-link>
        </footer>
      </div>
    </template>
    <template v-else>
      <div class="card card-margin">
        <header class="card-header clickable">
          <p class="card-header-title is-inline is-unselectable has-text-weight-normal">
            This {{ selectionData.type }} does not exist in {{ model.short_name }}.
            Email us at contact@metabolicatlas.org
          </p>
        </header>
      </div>
    </template>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { capitalize, reformatStringToLink, idfy } from '../../../helpers/utils';
import { chemicalFormula, chemicalReaction } from '../../../helpers/chemical-formatters';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'SidebarDataPanels',
  props: {
    dim: String,
    mapType: String,
    mapName: String,
    mapsData: Object,
    selectionData: Object,
    loading: Boolean,
  },
  data() {
    return {
      errorMessage: '',
      selectedElementDataKeys: {
        metabolite: [
          { name: 'name' },
          { name: 'model_name', display: 'Model&nbsp;name' },
          { name: 'formula' },
          { name: 'compartment' },
          { name: 'synonyms', display: 'Synonym(s)' },
        ],
        gene: [
          { name: 'name', display: 'Gene&nbsp;name' },
          { name: 'alternate_name', display: 'Alt&nbsp;name' },
          { name: 'synonyms', display: 'Synonym(s)' },
        ],
        reaction: [
          { name: 'equation' },
          { name: 'subsystem', display: 'Subsystem(s)' },
          { name: 'reactionreactant_set', display: 'Reactant(s)' },
          { name: 'reactionproduct_set', display: 'Product(s)' },
        ],
      },
      showMapCardContent: true,
      showSelectionCardContent: true,
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
  methods: {
    getGemBrowserLinkId() {
      if (this.mapType === 'compartment') {
        return this.mapsData.compartments[this.mapName].compartment || this.mapsData.compartments[this.mapName].id;
      }
      return this.mapsData.subsystems[this.mapName].subsystem || this.mapsData.subsystems[this.mapName].id;
    },
    selectionHasNoData() {
      if (!(this.selectionData.type
          in this.selectedElementDataKeys)) {
        return true;
      }
      for (let i = 0;
        i < this.selectedElementDataKeys[this.selectionData.type].length;
        i += 1) {
        const k = this.selectedElementDataKeys[this.selectionData.type][i];
        if (k.name in this.selectionData.data
          && this.selectionData.data[k.name]) {
          return false;
        }
      }
      return true;
    },
    isAvailableSubsystemMap(name) {
      // get the name from the svg
      return this.mapsData.subsystems[idfy(name)]
        && this.mapsData.subsystems[idfy(name)].sha;
    },
    capitalize,
    reformatStringToLink,
    chemicalFormula,
    chemicalReaction,
    idfy,
  },
};
</script>

<style lang="scss">
  #sidebar_mapviewer {
    .content p:not(:last-child) {
      margin-bottom: 0.3em;
    }
  }
</style>
