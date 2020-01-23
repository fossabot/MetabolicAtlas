<template>
  <div v-if="hasExternalID">
    <h4 class="title is-4">External databases</h4>
    <table v-if="component && Object.keys(component).length != 0" id="ed-table" class="table is-fullwidth">
      <!-- eslint-disable-next-line vue/no-template-key -->
      <template v-for="el in externalIDTableKey[type][model.database_name]">
        <tr v-if="component[el.name]" :key="el.name">
          <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis"
              v-html="el.display"></td>
          <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
          <td>
            <template v-if="el.link">
              <a :href="`${component[el.link]}`" target="_blank">{{ component[el.name] }}</a>
            </template>
            <template v-else>
              {{ component[el.name] }}
            </template>
          </td>
        </tr>
      </template>
    </table>
  </div>
</template>

<script>
import { reformatTableKey } from '../../../helpers/utils';

export default {
  name: 'ExtIdTable',
  props: {
    model: Object,
    component: Object,
    type: String,
  },
  data() {
    return {
      externalIDTableKey: {
        reaction: {
          human1: [
            { name: 'kegg_id', display: 'KEGG', link: 'kegg_link' },
            { name: 'bigg_id', display: 'BiGG', link: 'bigg_link' },
            { name: 'reactome_id', display: 'Reactome', link: 'reactome_link' },
            { name: 'metanetx_id', display: 'MetaNetX', link: 'metanetx_link' },
            { name: 'hmr2_id', display: 'HMR2' },
            { name: 'recon3d_id', display: 'Recon3D' },
          ],
          yeast8: [],
        },
        metabolite: {
          human1: [
            { name: 'kegg_id', display: 'KEGG', link: 'kegg_link' },
            { name: 'bigg_id', display: 'BiGG', link: 'bigg_link' },
            { name: 'hmdb_id', display: 'HMDB', link: 'hmdb_link' },
            { name: 'chebi_id', display: 'ChEBI', link: 'chebi_link' },
            { name: 'pubchem_id', display: 'PubChem', link: 'pubchem_link' },
            { name: 'lipidmaps_id', display: 'Lipidmaps', link: 'lipidmaps_link' },
            { name: 'metanetx_id', display: 'MetaNetX', link: 'metanetx_link' },
          ],
          yeast8: [
          ],
        },
        gene: {
          human1: [
            { name: 'id', display: 'Ensembl', link: 'ensembl_link' },
            { name: 'hpa_id', display: 'Protein Atlas', link: 'hpa_link' },
            { name: 'uniprot_id', display: 'Uniprot', link: 'uniprot_link' },
            { name: 'ncbi_id', display: 'NCBI', link: 'ncbi_link' },
          ],
          yeast8: [],
        },
      },
    };
  },
  computed: {
    hasExternalID() {
      for (let i = 0; i < this.externalIDTableKey[this.type][this.model.database_name].length; i += 1) {
        const item = this.externalIDTableKey[this.type][this.model.database_name][i];
        if (this.component[item.name]) {
          return true;
        }
      }
      return false;
    },
  },
  methods: {
    reformatTableKey,
  },
};
</script>

<style lang="scss"></style>
