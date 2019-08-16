<template>
  <div id="sidebar_mapviewer">
    <div class="column" v-if="tissue">
      <div class="card">
        <header class="card-header clickable" @click.prevent="showLvlCardContent = !showLvlCardContent">
          <p class="card-header-title is-inline">
            RNA levels for&nbsp;<i class="is-capitalized">{{ tissue }}</i>
          </p>
          <a href="#" class="card-header-icon" aria-label="more options">
            <span class="icon">
              <i aria-hidden="true" :class="[showLvlCardContent ? 'fa-caret-down' : 'fa-caret-right', 'fa']"></i>
            </span>
          </a>
        </header>
        <div v-html="RNAExpressionLegend" v-show="showLvlCardContent"></div>
      </div>
    </div>
    <div class="column" v-if="mapName">
      <div class="card">
        <header class="card-header" @click.prevent="showMapCardContent = !showMapCardContent">
          <p class="card-header-title is-capitalized is-inline">
            {{ mapType }}:
            <i>{{ mapsData.compartments[mapName] ? mapsData.compartments[mapName].name : mapsData.subsystems[mapName] ? mapsData.subsystems[mapName].name : '' }}</i>
          </p>
        </header>
        <footer class="card-footer">
          <router-link class="is-paddingless is-info is-outlined card-footer-item has-text-centered" :to="{ path: `/explore/gem-browser/${model.database_name}/${mapType}/${ mapsData.compartments[mapName] ? mapsData.compartments[mapName].id : mapsData.subsystems[mapName] ? mapsData.subsystems[mapName].id : '' }`}">
            <span class="icon is-large"><i class="fa fa-database fa-lg"></i></span>
            <span>{{ messages.gemBrowserName }}</span>
          </router-link>
        </footer>
      </div>
    </div>
    <template v-if="loading">
      <div class="loading">
        <a class="button is-large is-loading"></a>
      </div>
    </template>
    <template v-else>
      <div class="column">
        <div class="card" v-if="selectionData.data && mapType !== 'subsystem' && selectionData.type == 'subsystem'">
          <header class="card-header">
            <p class="card-header-title is-capitalized is-inline is-unselectable">
              {{ selectionData.type }}: <i>{{ selectionData.data.id }}</i>
            </p>
          </header>
          <footer class="card-footer" v-if="!selectionData.error">
            <router-link class="is-paddingless is-info is-outlined card-footer-item has-text-centered" :to="{ path: `/explore/gem-browser/${model.database_name}/${selectionData.type}/${idfy(selectionData.data.id)}`}">
              <span class="icon is-large"><i class="fa fa-database fa-lg"></i></span>
              <span>{{ messages.gemBrowserName }}</span>
            </router-link>
            <div class="is-paddingless is-primary is-outlined card-footer-item has-text-centered"
              @click="(mapsData.subsystems[idfy(selectionData.data.id)] && mapsData.subsystems[idfy(selectionData.data.id)].sha) && showSubsystem(idfy(selectionData.data.id))"
              :disabled="!mapsData.subsystems[idfy(selectionData.data.id)] || !mapsData.subsystems[idfy(selectionData.data.id)].sha">
              <span class="icon is-large"><i class="fa fa-map-o fa-lg"></i></span>
              <span>Load map</span>
            </div>
          </footer>
        </div>
        <div class="card" v-else-if="selectionData.data && ['metabolite', 'gene', 'reaction'].includes(selectionData.type)">
          <header class="card-header clickable" v-if="!selectionData.error" @click.prevent="showSelectionCardContent = !showSelectionCardContent">
            <p class="card-header-title is-inline is-capitalized is-unselectable">
              {{ selectionData.type }}: <i>{{ selectionData.data.id }}</i>
            </p>
            <a href="#" class="card-header-icon" aria-label="more options">
              <span class="icon">
                <i aria-hidden="true" :class="[showSelectionCardContent ? 'fa-caret-down' : 'fa-caret-right', 'fa']"></i>
              </span>
            </a>
          </header>
          <div class="card-content card-content-compact" v-show="showSelectionCardContent">
            <div class="content" v-if="!selectionData.error">
              <p v-if="selectionData.data['rnaLvl'] != null">
                <span class="has-text-weight-bold">RNA&nbsp;level:&nbsp;</span><span>{{ selectionData.data['rnaLvl'] }}</span>
              </p>
              <template v-for="item in selectedElementDataKeys[model.database_name][selectionData.type]"
                v-if="selectionData.data[item.name] != null || item.name === 'external_ids'" >
                <template v-if="item.name === 'external_ids'">
                  <span class="has-text-weight-bold"
                  v-if="hasExternalIDs(item.value)">{{ item.display || item.name}} :</span>
                  <p v-if="hasExternalIDs(item.value)">
                    <template v-for="eid in item.value" v-if="selectionData.data[eid[1]] && selectionData.data[eid[2]]">
                      <span class="has-text-weight-bold">{{ capitalize(eid[0]) }}:</span>
                      <span v-html="reformatStringToLink(selectionData.data[eid[1]], selectionData.data[eid[2]])"></span><br>
                    </template>
                  </p>
                </template>
                <template v-else-if="['aliases', 'subsystem_str'].includes(item.name)">
                  <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span><p>
                  <template v-for="s in selectionData.data[item.name].split('; ')">
                    &ndash;&nbsp;{{ s }}<br>
                  </template></p>
                </template>
                <template v-else-if="['reactionreactant_set', 'reactionproduct_set'].includes(item.name)">
                  <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span>
                  <p>
                    <template v-for="s in selectionData.data[item.name]">
                      &ndash;&nbsp;{{ s[`${item.name.includes('reactant') ? 'reactant' : 'product' }`].full_name }}<br>
                    </template>
                  </p>
                </template>
                <template v-else-if="item.name === 'equation'">
                  <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"></span><br>
                  <span v-html="chemicalReaction(selectionData.data[item.name], selectionData.data['is_reversible'])"></span></p>
                </template>
                <template v-else-if="item.name === 'formula'">
                  <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ': '"></span>
                  <span v-html="chemicalFormula(selectionData.data[item.name], selectionData.data.charge)"></span></p>
                </template>
                <template v-else>
                  <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"></span>
                  {{ selectionData.data[item.name] }}</p>
                </template>
              </template>
              <template v-if="selectionHasNoData()">
                {{ messages.noInfoAvailable }}
              </template>
            </div>
          </div>
          <footer class="card-footer" v-if="!selectionData.error">
            <router-link class="is-paddingless is-info is-outlined card-footer-item has-text-centered" :to="{ path: `/explore/gem-browser/${model.database_name}/${selectionData.type}/${idfy(selectionData.data.id)}`}">
              <span class="icon is-large"><i class="fa fa-database fa-lg"></i></span>
              <span>{{ messages.gemBrowserName }}</span>
            </router-link>
          </footer>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { capitalize, reformatStringToLink, idfy } from '../../../helpers/utils';
import { chemicalFormula, chemicalReaction } from '../../../helpers/chemical-formatters';
import { default as messages } from '../../../helpers/messages';
import { default as EventBus } from '../../../event-bus';

export default {
  name: 'sidebar-data-panels',
  props: ['model', 'dim', 'tissue', 'mapType', 'mapName', 'mapsData', 'selectionData', 'loading'],
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
            { name: 'reactionproduct_set', display: 'Products'  },
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
            { name: 'reactionproduct_set', display: 'Products'  },
          ],
        },
      },
      showLvlCardContent: true,
      showMapCardContent: true,
      showSelectionCardContent: true,
      RNAExpressionLegend: '',
      messages,
    };
  },
  created() {
    EventBus.$off('updateRNAExpressionLegend');

    EventBus.$on('updateRNAExpressionLegend', (legend) => {
      this.RNAExpressionLegend = legend;
    });
  },
  methods: {
    hasExternalIDs(keys) {
      for (const eid of keys) {
        if (this.selectionData.data[eid[1]] && this.selectionData.data[eid[2]]) {
          return true;
        }
      }
      return false;
    },
    selectionHasNoData() {
      if (!(this.selectionData.type in
          this.selectedElementDataKeys[this.model.database_name])) {
        return true;
      }
      for (const k of this.selectedElementDataKeys[this.model.database_name][this.selectionData.type]) {  // eslint-disable-line max-len
        if (k.name in this.selectionData.data &&
          this.selectionData.data[k.name]) {
          return false;
        }
      }
      return true;
    },
    showSubsystem(id) {
      EventBus.$emit('showAction', 'subsystem', id, [], false);
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
