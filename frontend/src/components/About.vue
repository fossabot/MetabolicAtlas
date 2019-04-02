<template>
  <section class="section section-no-top extended-section">
    <div class="container is-size-5">
      <h2 class="title is-2">The Metabolic Atlas</h2>
      <div class="columns is-variable is-8">
        <div class="column is-half has-text-justified">
          <p>
            Metabolic Atlas project is headed by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Professor Jens Nielsen</a>, <a href="https://www.sysbio.se">Division of Systems and Synthetic Biology</a>,  Department of Biology and Biological Engineering at the <a href="https://www.chalmers.se" target="_new">Chalmers University of Technology</a>.<br><br>

            Metabolic Atlas is a freely available electronic database containing detailed information about a set of GEMs, especially <router-link :to="{ name: 'browserRoot', params: {model: 'human1'} }">Human1</router-link> and <router-link :to="{ name: 'browserRoot', params: {model: 'yeast8'} }">Yeast8</router-link>. These are two reference models containing all possible reactions that could occur in human, and yeast, respectively.<br><br>

            The research focus of the content of this website is <b>metabolism in a systems biology context</b>. The goal is to collect many curated Genome-Scale Metabolic Models (GEMs), and to bring these models closer to <a href="https://en.wikipedia.org/wiki/FAIR_data" target="_new">FAIR principles</a>. To this end, the website also provides visualisations and comparisons of the GEMs, and links to <a href="resources">resources</a>: algorithms, other databases, and more general software applications (like RAVEN and PIANO).<br><br>

            Metabolic Atlas is intended to be used for applications in metabolomics, clinical chemistry, biomarker discovery and general education. In short, the vision is to create a one-stop-shop for everything metabolism related, starting with <a href="https://www.sysbio.se/labs/nielsen/#publications">the publications of the Nielsen lab</a>.<br><br>

            For versions and release notes of the software behind Metabolic Atlas, <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases" target="_blank">check the GitHub page</a>. The integrated models are also on GitHub, for links check our <router-link :to="{ name: 'gems' }">GEMs Repository</router-link>.
          </p>
          <h4 class="subtitle is-size-4">External resources</h4>
          <p>Metabolic Atlas would not be possible without the following excellent sources of information: <a href="http://proteinatlas.org" target="_blank">The Human Protein Atlas</a>, <a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</a>, <a href="http://www.uniprot.org" target="_blank">UniProt</a>, <a href="http://www.hmdb.ca/" target="_blank">The Human Metabolome Database</a>.</p>
        </div>
        <div class="column is-half has-text-justified">
          <div class="box">
            <p class="subtitle is-size-4 has-text-primary has-text-centered">Citing the Metabolic Atlas</p>
            <p>Paper under consideration</p>
            <!-- <p>
              <a href="" target="_blank">APA style reference with DOI</a><br><br>
              Abstract here
              <br><br>
              Genome scale metabolic model in the publication <a @click="viewGem()">Human1</a>
            </p> -->
          </div><br>
          <img width="100%" src="../assets/group_18a.jpg">
          <center>The SysBio group 2018</center>
        </div>
      </div>
      <div class="columns is-variable is-8">
        <div class="column has-text-justified">
          <h4 class="subtitle is-size-4">Contact</h4>
          <p>
            For any questions, comments or suggestions please contact <a href="mailto:">contact[at]metabolicatlas.org</a>
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>

import { default as EventBus } from '../event-bus';

export default {
  name: 'about',
  methods: {
    viewGem() {
      this.$router.push({ name: 'gems' });
      EventBus.$emit('viewGem', 'Human1');
    },
  },
};
</script>

<style lang="scss">
</style>
