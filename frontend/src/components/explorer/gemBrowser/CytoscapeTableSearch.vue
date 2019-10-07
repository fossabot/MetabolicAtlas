<template>
  <div class="table-search">
    <p class="control">
      <input v-model="term" class="input" type="text" placeholder="Search in table" @input="search">
    </p>
  </div>
</template>

<script>

export default {
  name: 'CytoscapeTableSearch',
  props: {
    reset: Function,
  },
  data() {
    return {
      term: '',
      isSearching: false,
    };
  },
  methods: {
    clearSearch() {
      this.term = '';
      this.reset();
      this.isSearching = false;
    },
    search() {
      this.$emit('search', this.term);
      this.isSearching = this.term; // used as true/false
    },
  },
};

</script>

<style lang="sass"></style>
