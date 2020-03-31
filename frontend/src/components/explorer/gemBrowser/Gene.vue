<template>
  <div class="connected-metabolites">
    <div v-if="componentNotFound" class="columns is-centered">
      <notFound :type="type" :component-id="geneId"></notFound>
    </div>
    <div v-else>
      <div class="container columns">
        <div class="column">
          <h3 class="title is-3">
            <span class="is-capitalized">{{ type }}</span> {{ gene.geneName }}
          </h3>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div class="columns is-multiline is-variable is-8">
            <div id="gene-details" class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
              <table v-if="gene && Object.keys(gene).length !== 0" class="table main-table is-fullwidth">
                <tr v-for="el in mainTableKey" :key="el.name">
                  <td v-if="'display' in el"
                      class="td-key has-background-primary has-text-white-bis"
                      v-html="el.display"></td>
                  <td v-else-if="el.name === 'id'"
                      class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
                  <td v-else
                      class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                  <td v-if="gene[el.name]">
                    <span v-if="'modifier' in el" v-html="el.modifier(gene)">
                    </span>
                    <span v-else>
                      {{ gene[el.name] }}
                    </span>
                  </td>
                  <td v-else> - </td>
                </tr>
              </table>
              <ExtIdTable :type="type" :external-dbs="gene.external_databases"></ExtIdTable>
            </div>
            <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
              <router-link class="button is-info is-fullwidth is-outlined"
                           :to="{ name: 'interPartner', params: { model: model.database_name, id: gene.id } }">
                <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
                <span>{{ messages.interPartName }}</span>
              </router-link>
              <br>
              <maps-available :id="geneId" :type="'gene'" :viewer-selected-i-d="gene.id" />
              <gem-contact :id="geneId" :type="type" />
            </div>
          </div>
          <reaction-table :source-name="geneId" :type="type" :show-subsystem="true" :selected-elm-id="geneName"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import GemContact from '@/components/shared/GemContact';
import NotFound from '@/components/NotFound';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';
import { reformatTableKey } from '@/helpers/utils';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Gene',
  components: {
    NotFound,
    MapsAvailable,
    ReactionTable,
    GemContact,
    ExtIdTable,
  },
  data() {
    return {
      messages,
      showLoader: true,
      showReactionLoader: true,
      geneId: '',
      type: 'gene',
      mainTableKey: [
        { name: 'id' },
        { name: 'geneName', display: 'Gene&nbsp;name' },
        { name: 'alternate_name', display: 'Alternate&nbsp;name' },
        { name: 'synonyms' },
        { name: 'function' },
      ],
      limitReaction: 200,
      componentNotFound: false,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      gene: state => state.genes.gene,
    }),
    ...mapGetters({
      geneName: 'genes/geneName',
    }),
  },
  async beforeMount() {
    if (this.$route.params.id) {
      this.geneId = this.$route.params.id;
      this.showLoader = true;
      try {
        const payload = { model: this.model.database_name, id: this.geneId };
        await this.$store.dispatch('genes/getGeneData', payload);
        this.showLoader = false;
        this.componentNotFound = false;
      } catch {
        this.showLoader = false;
        this.reactions = [];
        this.componentNotFound = true;
        document.getElementById('search').focus();
      }
    }
  },
  methods: {
    reformatTableKey(k) { return reformatTableKey(k); },
  },
};

</script>

<style lang="scss">
</style>
