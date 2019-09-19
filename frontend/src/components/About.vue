<template>
  <!-- eslint-disable max-len -->
  <section class="section extended-section is-size-5">
    <div class="container">
      <h2 class="title is-2">Metabolic Atlas</h2>
      <div class="columns is-variable is-8">
        <div class="column is-half has-text-justified">
          <p>
          </p><div class="box is-hidden-tablet">
            <p class="subtitle has-text-weight-bold is-size-4 has-text-primary has-text-centered">Citing Metabolic Atlas</p>
            <i>Article under consideration</i>
            <!-- <p>
                <a href="" target="_blank">APA style reference with DOI</a><br><br>
                Abstract here
                <br><br>
                Genome scale metabolic model in the publication <a @click="viewGem()">Human1</a>
              </p> -->
          </div>
          The Metabolic Atlas project is headed by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Professor Jens Nielsen</a>, <a href="https://www.sysbio.se">Division of Systems and Synthetic Biology</a>, Department of Biology and Biological Engineering at the <a href="https://www.chalmers.se" target="_new">Chalmers University of Technology</a>. The platform is developed by members of <a href="https://www.chalmers.se/en/researchinfrastructure/csb/Pages/default.aspx">Computational Systems Biology Infrastructure</a> at Chalmers University of Technology and <a href="https://nbis.se" target="blank">National Bioinformatics Infrastructure Sweden</a>.<br><br>

          Metabolic Atlas is a freely available resource containing detailed information about a set of open-source  Genome-Scale Metabolic Models (GEMs), specifically <router-link :to="{ name: 'browserRoot', params: {model: 'human1'} }">Human1</router-link> and <router-link :to="{ name: 'browserRoot', params: {model: 'yeast8'} }">Yeast8</router-link>. These are two reference models containing all possible reactions that could occur in human, and yeast, respectively.<br><br>

          The research focus of the content of this website is <b>metabolism in a systems biology context</b>. The goal is to collect many curated GEMs, and to bring these models closer to <a href="https://en.wikipedia.org/wiki/FAIR_data" target="_new">FAIR principles</a>. To this end, the website also provides visualisations and comparisons of the GEMs, and links to <a href="resources">resources</a>: algorithms, other databases, and more general software applications (like RAVEN and PIANO).<br><br>

          Metabolic Atlas is intended to be used for applications in metabolomics, clinical chemistry, biomarker discovery and general education. In short, the vision is to create a one-stop-shop for everything metabolism related, starting with <a href="https://www.sysbio.se/labs/nielsen/#publications">the publications of the Nielsen lab</a>.<br><br>

          For versions and release notes of the software behind Metabolic Atlas, <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases" target="_blank">check the GitHub page</a>. The current software development team members are Pierre-Etienne Cholley and Mihail Anton. Past and more detailed contributions are <a href="https://github.com/SysBioChalmers/MetabolicAtlas/graphs/contributors" target="_blank">shown on GitHub</a>. The integrated models are also available on GitHub, check our <router-link :to="{ name: 'gems' }">GEM Repository</router-link> for links to those.<br><br>

          <p>Metabolic Atlas would not be possible without the following excellent Elixir resources: <a href="https://proteinatlas.org" target="_blank">The Human Protein Atlas</a>, <a href="https://www.ensembl.org/" target="_blank">Ensembl</a>, <a href="https://www.uniprot.org" target="_blank">UniProt</a>, <a href="https://europepmc.org" target="_blank">Europe PMC</a>, <a href="https://identifiers.org" target="_blank">Identifiers.org</a>, <a href="https://www.ebi.ac.uk/chebi" target="_blank">ChEBi</a> and other essential sources of information: <a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</a>,  <a href="http://www.hmdb.ca/" target="_blank">The Human Metabolome Database</a>, <a href="https://www.metanetx.org" target="_blank">MetaNetX</a>, <a href="http://bigg.ucsd.edu" target="_blank">BiGG</a>, <a href="https://www.ncbi.nlm.nih.gov" target="_blank">NCBI</a>.
          </p>
        </div>
        <div class="column is-half has-text-justified content">
          <div class="box is-hidden-mobile">
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
          <h4 class="title is-4">Scientific Advisors</h4>
          <nav id="advisors" class="level">
            <div class="level-left">
              <a class="level-item">
                <figure class="image is-64x64">
                  <img class="is-rounded" src="../assets/pic-jens.jpg" />
                </figure>
                Jens Nielsen
              </a>
              <a class="level-item">
                <figure class="image is-64x64">
                  <img class="is-rounded" src="../assets/pic-jon.jpg" />
                </figure>
                Jon Robinson
              </a>
            </div>
          </nav>
          <br>
          <h4 class="title is-4">Contact</h4>
          <p>For any questions, comments or suggestions please email us <a href="mailto:">contact [at] metabolicatlas [dot] org</a> .</p>
        </div>
      </div>
      <h2 class="title is-2">News</h2>
      <div class="timeline">
        <header class="timeline-header">
          <span class="tag is-large has-text-primary has-text-weight-bold">2020</span>
        </header>
        <template v-for="year in Object.keys(news).reverse()">
          <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
          <template v-for="newsItem in news[year]">
            <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
            <div class="timeline-item is-danger">
              <div class="timeline-marker is-primary" :class="{ 'is-icon' : newsItem.icon }">
                <i v-if="newsItem.icon" :class="`fa fa-${newsItem.icon}`"></i>
              </div>
              <div class="timeline-content">
                <p class="heading">{{ newsItem.date }}</p>
                <p v-html="newsItem.text"></p>
              </div>
            </div>
          </template>
          <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
          <header class="timeline-header">
            <span class="tag is-large has-text-primary has-text-weight-bold">{{ year }}</span>
          </header>
        </template>
      </div>
      <br>
      <div class="columns is-variable is-8">
        <div class="column has-text-justified content">
          <h2 id="privacy" class="title is-2">Privacy Notice</h2>
          <p>
            Metabolic Atlas gathers information about users solely to improve the usability and usefulness of the website. There are two types of cookies that are set by Metabolic Atlas: functionality cookies and tracking cookies.<br>
            Functionality cookies are used to personalize the appearence of the Metabolic Atlas.<br>
            Tracking cookies are used by our private analytics to track the users on our website. We use these to observe the anonymized behaviour on our website in order to improve it. We store partial IP, operating system, browser and browser language. This information is stored permanently and is not shared with any third party. To opt out, please set your browser to use the "DoNotTrack" header; doing this will disable the tracking.<br>
            Additionally, we use the services of HotJar.com. This is an additional independent tracking service, which can produce a screen capture of the interactions on our website. We use it for the purpose of figuring out how to improve our website. The data is stored for at most 3 months. To opt out, see the <a href="https://www.hotjar.com/legal/compliance/opt-out" target="_blank">instructions on their website</a>. HotJar adheres to GDPR, <a href="https://www.hotjar.com/legal/compliance/gdpr-commitment" target="_blank">see more on their website.</a>
          </p>

          <h2 class="title is-2">Terms of Use</h2>
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
  name: 'About',
  data() {
    return {
      news: {
        2019: [
          { date: '5 September 2019',
            text: 'Metabolic Atlas v1.4 enables gene expression comparison [will add more details]' },
          { date: '1 August 2019',
            text: 'Metabolic Atlas v1.3 [will add more details]' },
          { date: '25 June 2019',
            text: 'Metabolic Atlas is upgraded to v1.2 with Human1 updated to v1.1 [will add more details]' },
          { date: '29 May 2019',
            text: 'Metabolic Atlas is upgraded to v1.1 [will add more details]' },
          { date: '17 May 2019',
            text: 'Metabolic Atlas is publicly available as v1.0 [will add more details]',
            icon: 'flag' },
          { date: '5 May 2019',
            text: '<i>Human1</i> is integrated, with complete compartment maps, and a significant coverage of the subsystem maps.' },
        ],
        2018: [
          { date: 'December 2018',
            text: 'New manually curated maps for <i>Human1</i> are being created, and the MapViewer is faster when browsing these maps.' },
          { date: 'November 2018',
            text: 'Draft models of <i>Human1</i> and <i>Yeast8</i> have been integrated on the 23rd and 28th respectively.' },
          { date: 'September 2018',
            text: 'Development on Metabolic Atlas is coordinated by Mihail Anton from <a href="https://nbis.se" target="blank">NBIS</a> in close collaboration with  <a href="https://www.sysbio.se">SysBio</a>, headed by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Prof. Nielsen</a>.',
            icon: 'thumb-tack' },
        ],
        2017: [
          { date: 'September 2017',
            text: 'The project is coordinated by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Prof. Nielsen</a>.',
            icon: 'thumb-tack' },
        ],
        2016: [
          { date: 'September 2016',
            text: 'The framework behind Metabolic Atlas is coordinated by Lena Hansson from <a href="https://nbis.se" target="blank">NBIS</a> in close collaboration with  <a href="https://www.sysbio.se">SysBio</a>, under the direction of <a href="https://www.sysbio.se/labs/nielsen" target="_new">Prof. Nielsen</a>.',
            icon: 'thumb-tack' },
          { date: 'April 2016',
            text: 'Work on a new Atlas began in the GitHub repository, directed by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Prof. Nielsen</a>.',
            icon: 'thumb-tack' },
        ],
        2015: [
          { date: 'July 2015',
            text: 'A first Atlas focusing on human metabolism is made publicly available at <i>metabolicatlas.org</i>, with the associated publication <a href="https://academic.oup.com/database/article/doi/10.1093/database/bav068/2433201" target="_blank"><i>Human metabolic atlas: an online resource for human metabolism</i></a>.',
            icon: 'archive' },

        ],
      },
    };
  },
  methods: {
    viewGem() {
      this.$router.push({ name: 'gems' });
      EventBus.$emit('viewGem', 'Human1');
    },
  },
};
</script>

<style lang="scss">

#advisors{
  figure {
    margin: 0 1rem 0 0;
  }
  .level-item {
    justify-content: flex-start;
    margin: 0 4rem 0 0;
  }
}

</style>
