<template>
  <section class="section extended-section">
    <div class="container is-size-5">
      <h2 class="title is-2">Metabolic Atlas</h2>
      <div class="columns is-variable is-8">
        <div class="column is-half has-text-justified">
          <p>
            The Metabolic Atlas project is headed by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Professor Jens Nielsen</a>, <a href="https://www.sysbio.se">Division of Systems and Synthetic Biology</a>, Department of Biology and Biological Engineering at the <a href="https://www.chalmers.se" target="_new">Chalmers University of Technology</a>. The platform is developed by members of <a href="https://www.chalmers.se/en/researchinfrastructure/csb/Pages/default.aspx">Computational Systems Biology Infrastructure</a> at Chalmers University of Technology and <a href="https://nbis.se" target="blank">National Bioinformatics Infrastructure Sweden</a>.<br><br>

            Metabolic Atlas is a freely available resource containing detailed information about a set of open-source GEMs, specifically <router-link :to="{ name: 'browserRoot', params: {model: 'human1'} }">Human1</router-link> and <router-link :to="{ name: 'browserRoot', params: {model: 'yeast8'} }">Yeast8</router-link>. These are two reference models containing all possible reactions that could occur in human, and yeast, respectively.<br><br>

            The research focus of the content of this website is <b>metabolism in a systems biology context</b>. The goal is to collect many curated Genome-Scale Metabolic Models (GEMs), and to bring these models closer to <a href="https://en.wikipedia.org/wiki/FAIR_data" target="_new">FAIR principles</a>. To this end, the website also provides visualisations and comparisons of the GEMs, and links to <a href="resources">resources</a>: algorithms, other databases, and more general software applications (like RAVEN and PIANO).<br><br>

             Metabolic Atlas is intended to be used for applications in metabolomics, clinical chemistry, biomarker discovery and general education. In short, the vision is to create a one-stop-shop for everything metabolism related, starting with <a href="https://www.sysbio.se/labs/nielsen/#publications">the publications of the Nielsen lab</a>.<br><br>

             For versions and release notes of the software behind Metabolic Atlas, <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases" target="_blank">check the GitHub page</a>. The current software development team members are Pierre-Etienne Cholley and Mihail Anton. Past and more detailed contributions are <a href="https://github.com/SysBioChalmers/MetabolicAtlas/graphs/contributors" target="_blank">shown on GitHub</a>. The integrated models are also available on GitHub, check our <router-link :to="{ name: 'gems' }">GEM Repository</router-link> for links to those.<br><br>

             <p>Metabolic Atlas would not be possible without the following excellent Elixir resources: <a href="https://proteinatlas.org" target="_blank">The Human Protein Atlas</a>, <a href="https://www.ensembl.org/" target="_blank">Ensembl</a>, <a href="https://www.uniprot.org" target="_blank">UniProt</a>, <a href="https://europepmc.org" target="_blank">Europe PMC</a>, <a href="https://identifiers.org" target="_blank">Identifiers.org</a>, <a href="https://www.ebi.ac.uk/chebi" target="_blank">ChEBi</a> and other essential sources of information: <a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</a>,  <a href="http://www.hmdb.ca/" target="_blank">The Human Metabolome Database</a>, <a href="https://www.metanetx.org" target="_blank">MetaNetX</a>, <a href="http://bigg.ucsd.edu" target="_blank">BiGG</a>, <a href="https://www.ncbi.nlm.nih.gov" target="_blank">NCBI</a>.
          </p>
        </div>
        <div class="column is-half has-text-justified content">
          <div class="box">
            <p class="subtitle has-text-weight-bold is-size-4 has-text-primary has-text-centered">Citing Metabolic Atlas</p>
            <i>Article under consideration</i>
            <!-- <p>
              <a href="" target="_blank">APA style reference with DOI</a><br><br>
              Abstract here
              <br><br>
              Genome scale metabolic model in the publication <a @click="viewGem()">Human1</a>
            </p> -->
          </div>
          <img width="100%" src="../assets/group_18a.jpg">
          <center>The SysBio group 2018</center>
          <h4>Contact</h4>
          <p>
            For any questions, comments or suggestions please email us <a href="mailto:">contact [at] metabolicatlas [dot] org</a> .<br>
            Alternatively, find us at the <a href="https://www.sysbio.se/" target="blank">Division of Systems and Synthetic Biology</a> and <a href="https://nbis.se" target="blank">National Bioinformatics Infrastructure Sweden</a> .
          </p>
        </div>
      </div>
      <div class="columns is-variable is-8">
        <div class="column has-text-justified content">
          <h4 id="privacy">Privacy Notice</h4>
          <p>
            Metabolic Atlas gathers information about users solely to improve the usability and usefulness of the website. There are two types of cookies that are set by Metabolic Atlas: functionality cookies and tracking cookies.<br>
            Functionality cookies are used to personalize the appearence of the Metabolic Atlas.<br>
            Tracking cookies are used by our private analytics to track the users on our website. We use these to observe the anonymized behaviour on our website in order to improve it. We store partial IP, operating system, browser and browser language. This information is stored permanently and is not shared with any third party. To opt out, please set your browser to use the "DoNotTrack" header; doing this will disable the tracking.<br>
            Additionally, we use the services of HotJar.com. This is an additional independent tracking service, which can produce a screen capture of the interactions on our website. We use it for the purpose of figuring out how to improve our website. The data is stored for at most 3 months. To opt out, see the <a href="https://www.hotjar.com/legal/compliance/opt-out" target="_blank">instructions on their website</a>. HotJar adheres to GDPR, <a href="https://www.hotjar.com/legal/compliance/gdpr-commitment" target="_blank">see more on their website.</a>
          </p>

          <h4>Terms of Use</h4>
          <p>
            We do not guarantee the accuracy of any provided data, generated database, software or online service nor the suitability of databases, software and online services for any purpose.
            The content presented on Metabolic Atlas is contributed by members of the community who remain owners of said content.
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

<style lang="scss"></style>
