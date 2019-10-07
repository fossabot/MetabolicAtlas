<template>
  <div v-show="showTable" class="reactome column">
    <h4 class="title is-4">Reactions</h4>
    <div class="container">
      <p class="control field">
        <button class="button" :disabled="disableBut" @click="toggleExpandAllCompartment">
          {{ !expandAllCompartment ? "Expand to all compartments" : "Restrict to current compartment" }}
        </button>
      </p>
      <reaction-table v-show="!showLoader" :show-subsystem="true" :model="model" :limit="200"
                      :reactions="!expandAllCompartment ? reactions : reactionsAllcompartment"
                      :selected-elm-id="ID" :source-name="metaboliteID">
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

import axios from 'axios';
import Loader from '@/components/Loader';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';

export default {
  name: 'Reactome',
  components: {
    ReactionTable,
    Loader,
  },
  props: {
    model: Object,
    metaboliteID: String,
    disableBut: Boolean,
  },
  data() {
    return {
      errorMessage: '',
      reactions: [],
      reactionsAllcompartment: [],
      showLoader: true,
      showTable: false,
      expandAllCompartment: false,
      ID: '',
      reactomeID: '',
    };
  },
  watch: {
    metaboliteID() {
      if (this.metaboliteID) {
        this.ID = this.metaboliteID;
        this.reactomeID = '';
        this.reactions = [];
        this.reactionsAllcompartment = [];
        this.expandAllCompartment = false;
        this.loadReactions(this.ID);
      }
    },
  },
  methods: {
    loadReactions(ID) {
      if (this.reactomeID
          && ((this.expandAllCompartment && this.reactionsAllcompartment.length !== 0)
         || (!this.expandAllCompartment && this.reactions.length !== 0))) {
        this.reactomeID = ID;
        return;
      }
      this.showLoader = true;
      this.reactomeID = ID;
      let url = `${this.model.database_name}/metabolite/${ID}/get_reactions/`;
      if (this.expandAllCompartment) {
        url = `${this.model.database_name}/metabolite/${ID}/get_reactions/all_compartments/`;
      }
      axios.get(url)
        .then((response) => {
          this.errorMessage = '';
          if (this.expandAllCompartment) {
            this.reactionsAllcompartment = response.data;
          } else {
            this.reactions = response.data;
          }
          this.showTable = true;
          this.showLoader = false;
        })
        .catch(() => {
          this.showLoader = false;
          this.showTable = false;
        });
    },
    toggleExpandAllCompartment() {
      if (this.disableBut) {
        return;
      }
      this.expandAllCompartment = !this.expandAllCompartment;
      this.loadReactions(this.ID);
    },
  },
};

</script>

<style lang="scss">

</style>
