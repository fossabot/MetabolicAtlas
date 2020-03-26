<template>
  <div v-show="showTable" class="reactome column">
    <h4 class="title is-4">Reactions</h4>
    <div class="container">
      <p class="control field">
        <button class="button" :disabled="disableBut" @click="toggleExpandAllCompartment">
          {{ !expandAllCompartment ? "Expand to all compartments" : "Restrict to current compartment" }}
        </button>
      </p>
      <reaction-table v-show="!showLoader" :show-subsystem="true" :limit="200"
                      :reactions="reactions" :selected-elm-id="ID" :source-name="metaboliteID">
      </reaction-table>
      <div v-if="errorMessage" class="columns">
        <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
          {{ errorMessage }}
        </div>
      </div>
      <div v-else>
        <loader v-show="showLoader"></loader>
      </div>
    </div>
  </div>
</template>

<script>

import { mapState } from 'vuex';
import Loader from '@/components/Loader';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';

export default {
  name: 'Reactome',
  components: {
    ReactionTable,
    Loader,
  },
  props: {
    metaboliteID: String,
    disableBut: Boolean,
  },
  data() {
    return {
      errorMessage: '',
      showLoader: true,
      showTable: false,
      expandAllCompartment: false,
      ID: '',
      reactomeID: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      reactions: state => state.reactions.relatedReactions,
    }),
  },
  watch: {
    async metaboliteID() {
      if (this.metaboliteID) {
        this.ID = this.metaboliteID;
        this.reactomeID = '';
        this.$store.dispatch('reactions/clearRelatedReactions');
        this.expandAllCompartment = false;
        await this.loadReactions(this.ID);
      }
    },
  },
  methods: {
    async loadReactions(ID) {
      this.showLoader = true;
      this.reactomeID = ID;
      try {
        const payload = { model: this.model.database_name, id: ID, allCompartments: this.expandAllCompartment };
        await this.$store.dispatch('reactions/getRelatedReactionsForMetabolite', payload);
        this.errorMessage = '';
        this.showTable = true;
        this.showLoader = false;
      } catch {
        this.showLoader = false;
        this.showTable = false;
      }
    },
    async toggleExpandAllCompartment() {
      if (this.disableBut) {
        return;
      }
      this.expandAllCompartment = !this.expandAllCompartment;
      await this.loadReactions(this.ID);
    },
  },
};

</script>

<style lang="scss">

</style>
