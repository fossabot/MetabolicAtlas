<template>
  <section class="extended-section">
    <div class="container">
      <div id="search-table">
        <div class="columns">
          <div class="column has-text-centered content">
            <br>
            <h3 class="title is-3">Search within all integrated GEMs</h3>
            <h4 class="subtitle is-4 has-text-weight-normal">for reactions, metabolites, genes, subsystems and compartments</h4>
          </div>
        </div>
        <div class="columns is-centered">
          <div class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile control">
            <div id="input-wrapper">
              <p class="control has-icons-right has-icons-left">
                <input id="search" class="input" type="text" v-model="searchTerm"
                  placeholder="Example: uracil, SULT1A3, ATP => cAMP + PPi, Acyl-CoA hydrolysis" v-on:keyup.enter="updateSearch()">
                <span class="has-text-danger icon is-small is-right" v-show="this.showSearchCharAlert" style="width: 200px">
                  Type at least 2 characters
                </span>
                <span class="icon is-medium is-left">
                  <i class="fa fa-search"></i>
                </span>
              </p>
            </div>
          </div>
        </div>
        <div>
          <div class="tabs is-boxed is-fullwidth" v-if="showTabType">
            <ul>
              <li :disabled="resultsCount[tab] === 0"
              :class="[{'is-active has-text-weight-semibold': showTab(tab) && resultsCount[tab] !== 0 }, { 'is-disabled': resultsCount[tab] === 0 }]"
              v-for="tab in tabs" @click="resultsCount[tab] !== 0 ? showTabType=tab : ''">
                <a class="is-capitalized">
                  {{ tab }}s&nbsp;
                  <span v-if="resultsCount[tab] !== 0">({{ resultsCount[tab] }})</span>
                </a>
              </li>
            </ul>
          </div>
          <loader v-show="loading && searchTerm !== ''"></loader>
          <div v-show="!loading">
            <div v-if="Object.keys(searchResults).length === 0" class="column is-offset-3 is-6">
              <div v-if="searchedTerm" class="has-text-centered notification">
                {{ messages.searchNoResult }} for <i>{{ searchedTerm }}</i>
              </div>
              <div class="content">
                <div class="has-text-centered">Search using the following parameters:</div>
                <span>Metabolites by:</span>
                <ul>
                  <li>ID</li>
                  <li>Name or aliases</li>
                  <li>Formula (without charge)</li>
                  <li>External identifiers</li>
                </ul>
                <span>Genes by:</span>
                <ul>
                  <li>ID</li>
                  <li>Name or aliases</li>
                  <li>External identifiers</li>
                </ul>
                <span>Reactions by:</span>
                <ul>
                  <li>ID</li>
                  <li>Equation (view the <router-link :to="{ 'path': '/documentation', hash:'Global-search'}">documentation</router-link> for more information)</li>
                  <li>EC code</li>
                  <li>External identifiers</li>
                </ul>
                <span>Subsystem and compartment by:</span>
                <ul>
                  <li>name</li>
                  <li>External identifiers (subsystem only)</li>
                </ul>
                <br>
                <div class="has-text-centered"><u>External identifiers and aliases may be missing if they are not provided with the models.</u></div>
              </div>
            </div>
            <template v-for="(header, index) in tabs">
              <div v-show="showTab(header) && resultsCount[header] !== 0">
                <vue-good-table ref="searchTables"
                  :columns="columns[header]" :rows="rows[header]"
                  :sort-options="{ enabled: true }" styleClass="vgt-table striped bordered" :paginationOptions="tablePaginationOpts">

                  <div slot="table-actions">
                    <a class="button is-primary" style="margin: 0.3rem 1rem;" @click="exportToTSV(header, index)">
                      <span class="icon is-large"><i class="fa fa-download"></i></span>
                      <span>Export to TSV</span>
                    </a>
                  </div>
                  <template slot="table-row" slot-scope="props">
                    <template v-if="props.column.field == 'model'">
                      {{ props.formattedRow[props.column.field].name }}
                    </template>
                    <template v-else-if="props.column.field === 'equation'">
                      <span v-html="reformatEqSign(props.formattedRow[props.column.field], false)"></span>
                    </template>
                    <template v-else-if="props.column.field === 'formula'">
                      <span v-html="formulaFormater(props.row[props.column.field], props.row.charge)"></span>
                    </template>
                    <template v-else-if="['name', 'id'].includes(props.column.field)">
                      <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/${header}/${props.row.id}` }">
                        {{ props.row.name || props.row.id }}
                      </router-link>
                    </template>
                    <template v-else-if="props.column.field === 'subsystem'">
                      <template v-if="props.formattedRow[props.column.field].length === 0">
                        {{ "" }}
                      </template>
                      <template v-else v-for="(sub, i) in props.formattedRow[props.column.field]">
                        <template v-if="i != 0">; </template>
                        <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/subsystem/${idfy(sub)}` }"> {{ sub }}</router-link>
                      </template>
                    </template>
                    <template v-else-if="props.column.field === 'compartment'">
                      <template v-if="props.formattedRow[props.column.field].length === 0">
                        {{ "" }}
                      </template>
                      <template v-else v-if="['subsystem', 'gene'].includes(header)">
                        <template v-for="(comp, i) in props.formattedRow[props.column.field]">
                          <template v-if="i != 0">; </template>
                          <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/compartment/${idfy(comp)}` }"> {{ comp }}</router-link>
                        </template>
                      </template>
                      <template v-else-if="header === 'reaction'">
                        <template v-for="(RP, i) in props.formattedRow[props.column.field].split(' => ')">
                          <template v-if="i != 0"> &#8658; </template>
                            <template v-for="(compo, j) in RP.split(' + ')">
                              <template v-if="j != 0"> + </template>
                              <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/compartment/${idfy(compo)}` }"> {{ compo }}</router-link>
                            </template>
                        </template>
                      </template>
                      <template v-else-if="Array.isArray(props.formattedRow[props.column.field])">
                        {{ props.formattedRow[props.column.field].join("; ") }}
                      </template>
                      <template v-else>
                         <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/compartment/${idfy(props.formattedRow[props.column.field])}` }"> {{ props.formattedRow[props.column.field] }}</router-link>
                      </template>
                    </template>
                    <template v-else-if="Array.isArray(props.formattedRow[props.column.field])">
                      {{ props.formattedRow[props.column.field].join("; ") }}
                    </template>
                    <template v-else>
                      {{ props.formattedRow[props.column.field] }}
                    </template>
                  </template>
                </vue-good-table>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>

import axios from 'axios';
import $ from 'jquery';
import { default as FileSaver } from 'file-saver';
import Loader from '@/components/Loader';
import { VueGoodTable } from 'vue-good-table';
import 'vue-good-table/dist/vue-good-table.css';
import { chemicalFormula } from '../helpers/chemical-formatters';
import { idfy, reformatEqSign, sortResults } from '../helpers/utils';
import { default as messages } from '../helpers/messages';

export default {
  name: 'search-table',
  components: {
    Loader,
    VueGoodTable,
  },
  data() {
    return {
      messages,
      tablePaginationOpts: {
        enabled: true,
        perPage: 50,
        position: 'both',
        perPageDropdown: [25, 50, 100, 200],
        dropdownAllowAll: false,
        setCurrentPage: 1,
        nextLabel: 'next',
        prevLabel: 'prev',
        rowsPerPageLabel: 'Rows per page',
        ofLabel: 'of',
      },
      tabs: [
        'metabolite',
        'gene',
        'reaction',
        'subsystem',
        'compartment',
      ],
      columns: {
        metabolite: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
              filterFn: (e, s) => e.id === s,
            },
            sortable: true,
          }, {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          }, {
            label: 'Formula',
            field: 'formula',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          }, {
            label: 'Subsystem',
            field: 'subsystem',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          },
        ],
        gene: [
          { label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
              filterFn: (e, s) => e.id === s,
            },
            sortable: true,
          }, {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          }, {
            label: 'Subsystem',
            field: 'subsystem',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          },
        ],
        reaction: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
              filterFn: (e, s) => e.id === s,
            },
            sortable: true,
          }, {
            label: 'ID',
            field: 'id',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          }, {
            label: 'Equation',
            field: 'equation',
            filterOptions: {
              enabled: true,
            },
            sortable: false,
          }, {
            label: 'Subsystem',
            field: 'subsystem',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Transport?',
            field: 'is_transport',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: false,
          },
        ],
        subsystem: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
              filterFn: (e, s) => e.id === s,
            },
            sortable: true,
          }, {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          }, {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Metabolites',
            field: 'metabolite_count',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          }, {
            label: 'Genes',
            field: 'gene_count',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          }, {
            label: 'Reactions',
            field: 'reaction_count',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
        ],
        compartment: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
              filterFn: (e, s) => e.id === s,
            },
            formatFn: this.getDisplayModelName,
            sortable: true,
          },
          {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: 'Metabolites',
            field: 'metaboliteCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: 'Genes',
            field: 'geneCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: 'Reactions',
            field: 'reactionCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: 'Subsystems',
            field: 'subsystemCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
        ],
      },
      resultsCount: {},
      searchTerm: '',
      searchedTerm: '',
      searchResults: [],
      showSearchCharAlert: false,
      showTabType: '',
      loading: false,
      rows: {
        metabolite: [],
        gene: [],
        reaction: [],
        subsystem: [],
        compartment: [],
      },
    };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.searchedTerm = to.query.term;
      vm.validateSearch(to.query.term);
      next();
    });
  },
  beforeRouteUpdate(to, from, next) {
    this.searchedTerm = to.query.term;
    this.validateSearch(to.query.term);
    next();
  },
  mounted() {
    $('#search').focus();
  },
  methods: {
    formulaFormater(formula, charge) {
      return chemicalFormula(formula, charge);
    },
    countResults() {
      for (const key of this.tabs) {
        this.resultsCount[key] = 0;
      }
      for (const el of Object.keys(this.searchResults)) {
        if (el in this.resultsCount) {
          this.resultsCount[el] = this.searchResults[el].length;
        }
      }
    },
    fillFilterFields() {
      const filterTypeDropdown = {
        metabolite: {
          model: {},
          compartment: {},
        },
        gene: {
          model: {},
          compartment: {},
        },
        reaction: {
          model: {},
          compartment: {},
          is_transport: {},
        },
        subsystem: {
          model: {},
          compartment: {},
        },
        compartment: {
          model: {},
        },
      };

      const rows = {
        metabolite: [],
        gene: [],
        reaction: [],
        subsystem: [],
        compartment: [],
      };

      // store choice only once in a dict
      for (const componentType of Object.keys(this.searchResults)) {
        const compoList = this.searchResults[componentType];
        // sort
        compoList.sort((a, b) => this.sortResults(a, b, this.searchedTerm));

        for (const el of compoList) { // e.g. results list for metabolites
          if (componentType === 'metabolite') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (field === 'subsystem') {
                for (const v of el[field]) {
                  if (!(v in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][v] = 1;
                  }
                }
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.id,
              model: el.model,
              name: el.name,
              formula: el.formula,
              charge: el.charge,
              subsystem: el.subsystem,
              compartment: el.compartment,
            });
          } else if (componentType === 'gene') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (['compartment', 'subsystem'].includes(field)) {
                for (const v of el[field]) {
                  if (!(v in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][v] = 1;
                  }
                }
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.id,
              model: el.model,
              name: el.name,
              subsystem: el.subsystem,
              compartment: el.compartment,
            });
          } else if (componentType === 'reaction') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'subsystem' && el[field]) {
                for (const v of el[field]) {
                  if (!(v in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][v] = 1;
                  }
                }
              } else if (field === 'compartment' && el[field]) {
                for (const compartment of el[field].split(/[^a-zA-Z0-9 ]+/)) {
                  if (compartment.trim() &&
                    !(compartment.trim() in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][compartment.trim()] = 1;
                  }
                }
              } else if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.id,
              model: el.model,
              equation: el.equation_wname,
              subsystem: el.subsystem,
              compartment: el.compartment,
              is_transport: el.is_transport ? 'Yes' : 'No',
            });
          } else if (componentType === 'subsystem') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'compartment') {
                for (const compartment of el[field]) {
                  if (!(compartment in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][compartment] = 1;
                  }
                }
              } else if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.name_id,
              model: el.model,
              name: el.name,
              compartment: el.compartment,
              metabolite_count: el.metabolite_count,
              gene_count: el.gene_count,
              reaction_count: el.reaction_count,
            });
          } else if (componentType === 'compartment') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.name_id,
              model: el.model,
              name: el.name,
              metaboliteCount: el.metabolite_count,
              geneCount: el.gene_count,
              reactionCount: el.reaction_count,
              subsystemCount: el.subsystem_count,
            });
          }
        }
        for (const field of Object.keys(filterTypeDropdown[componentType])) {
          if (field === 'model') {
            filterTypeDropdown[componentType][field] =
              Object.keys(filterTypeDropdown[componentType][field]).map(
                (e) => { const d = {}; d.value = e; d.text = filterTypeDropdown[componentType][field][e]; return d; } // eslint-disable-line
            );
          } else {
            filterTypeDropdown[componentType][field] =
              Object.keys(filterTypeDropdown[componentType][field]).map(
                (e) => {
                  let v = e;
                  if (v === 'true') {
                    v = 'Yes';
                  } else if (v === 'false') {
                    v = 'No';
                  }
                  return v;
                }
            ).sort();
          }
        }
      }
      // assign filter choices lists to the columns
      this.columns.metabolite[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.model;
      this.columns.metabolite[3].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.subsystem;
      this.columns.metabolite[4].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.compartment;

      this.columns.gene[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.gene.model;
      this.columns.gene[3].filterOptions.filterDropdownItems =
          filterTypeDropdown.gene.compartment;

      this.columns.reaction[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.model;
      this.columns.reaction[4].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.compartment;
      this.columns.reaction[5].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.is_transport;

      this.columns.subsystem[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.subsystem.model;
      this.columns.subsystem[2].filterOptions.filterDropdownItems =
          filterTypeDropdown.subsystem.system;
      this.columns.subsystem[3].filterOptions.filterDropdownItems =
          filterTypeDropdown.subsystem.compartment;

      this.columns.compartment[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.subsystem.model;
      this.rows = rows;
    },
    updateSearch() {
      this.$router.push({
        name: 'search',
        query: {
          term: this.searchTerm,
        },
      });
    },
    showTab(elementType) {
      return this.showTabType === elementType;
    },
    validateSearch(term) {
      this.searchTerm = term;
      this.showSearchCharAlert = false;
      this.searchResults = [];
      this.showTabType = '';
      this.searchResultsFiltered = {};
      if (this.searchTerm.length > 1) {
        this.search();
      } else if (this.searchTerm.length === 1) {
        this.showSearchCharAlert = true;
      }
    },
    search() {
      this.loading = true;
      const url = `all/search/${this.searchTerm}`;
      axios.get(url)
      .then((response) => {
        const localResults = {
          metabolite: [],
          gene: [],
          reaction: [],
          subsystem: [],
          compartment: [],
        };

        for (const model of Object.keys(response.data)) {
          const resultsModel = response.data[model];
          for (const resultType of ['metabolite', 'gene', 'reaction', 'subsystem', 'compartment']) {
            if (resultsModel[resultType]) {
              localResults[resultType] = localResults[resultType].concat(
                resultsModel[resultType].map(
                (e) => {
                  const d = e; d.model = { id: model, name: resultsModel.name }; return d;
                })
              );
            }
          }
        }
        this.searchResults = localResults;
      })
      .catch(() => {
        this.searchResults = [];
      })
      .then(() => {
        this.loading = false;
        // count types
        this.countResults();
        // get filters
        this.fillFilterFields();
        // select the active tab
        for (const key of Object.keys(this.resultsCount)) {
          if (this.resultsCount[key] !== 0) {
            this.showTabType = key;
            return;
          }
        }
      });
    },
    exportToTSV(type, index) {
      try {
        const rows = Array.from(this.$refs.searchTables[index].filteredRows[0].children);
        const header = [];
        let getHeader = false;
        let tsvContent = rows.map(e => {
            const data = [];
            for (let [key, value] of Object.entries(e)) {
              if (key !== 'vgt_id' && key !== 'originalIndex') {
                if (!getHeader) { header.push(key); }
                if (key === 'model') {
                  data.push(value.name);
                } else {
                  if (Array.isArray(value)) { value = value.join('; ') }
                  data.push(value);
                }
              }
            }
            if (!getHeader) { getHeader = true; }
            return data.join('\t') }
          ).join('\n');
        tsvContent = header.join('\t') + '\n' + tsvContent;
        const blob = new Blob([tsvContent], {
          type: 'data:text/tsv;charset=utf-8',
        });
        FileSaver.saveAs(blob, `${this.searchTerm}-${type}.tsv`);
      } catch (e) {
        this.errorMessage = e;
      }
    },
    idfy,
    chemicalFormula,
    reformatEqSign,
    sortResults,
  },
};

</script>

<style lang="scss">

#search-table {

  .tabs li.is-disabled {
    cursor: not-allowed;
    color: gray;
    opacity: 0.75;

    a {
      cursor: not-allowed;
    }
  }
}

</style>
