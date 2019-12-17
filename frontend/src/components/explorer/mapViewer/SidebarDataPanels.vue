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
                     :to="{ path: `/explore/gem-browser/${model.database_name}/${mapType}/${ mapsData.compartments[mapName] ? mapsData.compartments[mapName].id : mapsData.subsystems[mapName] ? mapsData.subsystems[mapName].id : '' }`}">  <!-- eslint-disable-line max-len -->
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
    <template v-else>
      <div v-if="selectionData.data && mapType !== 'subsystem' && selectionData.type == 'subsystem'"
           class="card card-margin">
        <header class="card-header">
          <p class="card-header-title is-capitalized is-inline is-unselectable">
            {{ selectionData.type }}: <i>{{ selectionData.data.id }}</i>
          </p>
        </header>
        <footer v-if="!selectionData.error" class="card-footer">
          <router-link class="is-paddingless is-info is-outlined card-footer-item has-text-centered"
                       :to="{ path: `/explore/gem-browser/${model.database_name}/${selectionData.type}/${idfy(selectionData.data.id)}`}">  <!-- eslint-disable-line max-len -->
            <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
            <span>{{ messages.gemBrowserName }}</span>
          </router-link>
          <template v-if="isAvailableSubsystemMap(selectionData.data.id)">
            <router-link
              class="is-paddingless is-primary is-outlined card-footer-item has-text-centered"
              :to="{ path: `/explore/map-viewer/${model.database_name}/${selectionData.type}/${idfy(selectionData.data.id)}?dim=2d` }">  <!-- eslint-disable-line max-len -->
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
        <header v-if="!selectionData.error"
                class="card-header clickable"
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
          <div v-if="!selectionData.error" class="content">
            <template v-for="item in selectedElementDataKeys[model.database_name][selectionData.type]
              .filter(i => selectionData.data[i.name] != null || i.name === 'external_ids')">
              <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
              <template v-if="item.name === 'external_ids' && hasExternalIDs(item.value)">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ item.display || item.name }} :</span>
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p>
                  <template v-for="eid in item.value.filter(e => selectionData.data[e[1]] && selectionData.data[e[2]])">
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    <span class="has-text-weight-bold">{{ capitalize(eid[0]) }}:</span>
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    <span v-html="reformatStringToLink(selectionData.data[eid[1]], selectionData.data[eid[2]])">
                      <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    </span><br>
                  </template>
                </p>
              </template>
              <template v-else-if="['aliases', 'subsystem_str'].includes(item.name)">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span><p>
                  <template v-for="s in selectionData.data[item.name].split('; ')">
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    &ndash;&nbsp;{{ s }}<br>
                  </template></p>
              </template>
              <template v-else-if="['reactionreactant_set', 'reactionproduct_set'].includes(item.name)">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span>
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p>
                  <template v-for="s in selectionData.data[item.name]">
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    &ndash;&nbsp;{{ s[`${item.name.includes('reactant') ? 'reactant' : 'product' }`].full_name }}<br>
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
        <footer v-if="!selectionData.error" class="card-footer">
          <router-link class="is-paddingless is-info is-outlined card-footer-item has-text-centered"
                       :to="{ path: `/explore/gem-browser/${model.database_name}/${selectionData.type}/${idfy(selectionData.data.id)}`}"> <!-- eslint-disable-line max-len -->
            <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
            <span>{{ messages.gemBrowserName }}</span>
          </router-link>
        </footer>
      </div>
    </template>
  </div>
</template>

<script>
import { capitalize, reformatStringToLink, idfy } from '../../../helpers/utils';
import { chemicalFormula, chemicalReaction } from '../../../helpers/chemical-formatters';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'SidebarDataPanels',
  props: {
    model: Object,
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
        human1: {
          metabolite: [
            { name: 'name' },
            { name: 'model_name', display: 'Model&nbsp;name' },
            { name: 'formula' },
            { name: 'compartment' },
            { name: 'aliases', display: 'Synonyms' },
          ],
          gene: [
            { name: 'name', display: 'Gene&nbsp;name' },
            { name: 'description', display: 'Description' },
            { name: 'gene_synonyms', display: 'Synonyms' },
          ],
          reaction: [
            { name: 'equation' },
            { name: 'subsystem_str', display: 'Subsystems' },
            { name: 'reactionreactant_set', display: 'Reactants' },
            { name: 'reactionproduct_set', display: 'Products' },
          ],
        },
        yeast8: {
          metabolite: [
            { name: 'name' },
            { name: 'model_name', display: 'Model&nbsp;name' },
            { name: 'formula' },
            { name: 'compartment' },
            { name: 'aliases', display: 'Synonyms' },
          ],
          gene: [
            { name: 'name', display: 'Gene&nbsp;name' },
            { name: 'description', display: 'Description' },
            { name: 'gene_synonyms', display: 'Synonyms' },
          ],
          reaction: [
            { name: 'equation' },
            { name: 'subsystem_str', display: 'Subsystems' },
            { name: 'reactionreactant_set', display: 'Reactants' },
            { name: 'reactionproduct_set', display: 'Products' },
          ],
        },
      },
      showMapCardContent: true,
      showSelectionCardContent: true,
      messages,
    };
  },
  methods: {
    hasExternalIDs(keys) {
      for (let i = 0; i < keys.length; i += 1) {
        const eid = keys[i];
        if (this.selectionData.data[eid[1]] && this.selectionData.data[eid[2]]) {
          return true;
        }
      }
      return false;
    },
    selectionHasNoData() {
      if (!(this.selectionData.type
          in this.selectedElementDataKeys[this.model.database_name])) {
        return true;
      }
      for (let i = 0;
        i < this.selectedElementDataKeys[this.model.database_name][this.selectionData.type].length;
        i += 1) {
        const k = this.selectedElementDataKeys[this.model.database_name][this.selectionData.type][i];
        if (k.name in this.selectionData.data
          && this.selectionData.data[k.name]) {
          return false;
        }
      }
      return true;
    },
    isAvailableSubsystemMap(name) {
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
