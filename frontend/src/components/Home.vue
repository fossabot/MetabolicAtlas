<template>
  <div class="extended-section">
    <section class="hero video container is-fullhd" style="max-width:100%; width:100%;">
      <div class="hero-video is-transparent is-block-mobile">
        <video poster="@/assets/banner_video.jpg"
               playsinline autoplay
               muted loop>
               <!-- <source src="https://ftp.metabolicatlas.org/.static/banner_video.mp4" type="video/mp4"> -->
        </video>
      </div>
      <div class="hero-body">
        <div class="container is-fullhd has-text-centered">
          <p class="is-size-2 title has-text-primary">METABOLIC ATLAS</p>
          <h3 class="is-size-3 has-text-gray">
            THE ATLAS FOR EXPLORATION OF METABOLISM
          </h3>
        </div>
      </div>
    </section>
    <section class="section">
      <div id="home" class="container is-fullhd">
        <div class="columns is-hidden-touch">
          <div class="column">
            <div class="card">
              <div class="columns is-mobile is-multiline margin-fix">
                <div id="menu-desktop"
                     class="column is-narrow has-background-primary has-text-weight-bold is-paddingless">
                  <aside class="menu">
                    <ul class="menu-list is-unselectable">
                      <li v-for="menuItem in menu" :key="menuItem.title">
                        <a :class="[ {'is-active' : menuItem.title === currentMenu.title}]"
                           @click="currentMenu = menuItem">
                          <span class="icon is-medium">
                            <i :class="`fa fa-${menuItem.icon}`"></i>
                          </span>
                          {{ menuItem.title }}
                        </a>
                      </li>
                    </ul>
                  </aside>
                </div>
                <div class="column more-padding is-v-aligned">
                  <p class="has-text-justified" v-html="currentMenu.text"></p>
                </div>
                <div class="column more-padding is-v-aligned">
                  <router-link :to="currentMenu.route">
                    <div class="card" :class="{ 'hoverable': currentMenu.cardLink}">
                      <img :src="currentMenu.img" :alt="currentMenu.title" />
                      <template v-if="currentMenu.cardLink">
                        <footer class="card-footer has-text-centered has-background-primary-lighter">
                          <a class="card-footer-item has-text-weight-bold">{{ currentMenu.cardLink }}</a>
                        </footer>
                      </template>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="columns is-hidden-desktop">
          <div class="column">
            <div class="card">
              <header class="card-header has-background-primary">
                <div class="card-header-title is-centered">
                  <div class="tabs is-medium is-centered">
                    <ul id="menu-mobile">
                      <li v-for="menuItem in menu" :key="menuItem.title">
                        <a :class="[ {'is-active' : menuItem.title === currentMenu.title}]"
                           @click="currentMenu = menuItem">
                          <i :class="`fa fa-${menuItem.icon} fa-lg`"></i>
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>
              </header>
              <div class="card-content">
                <p class="title has-text-centered">{{ currentMenu.title }}</p>
                <div class="columns is-variable is-4-tablet">
                  <div class="column is-half-tablet is-full-mobile">
                    <p class="has-text-justified" v-html="currentMenu.text"></p>
                  </div>
                  <div class="column is-half-tablet is-full-mobile more-padding is-v-aligned">
                    <router-link :to="currentMenu.route">
                      <div class="card" :class="{ 'card-selectable': currentMenu.cardLink}">
                        <img :src="currentMenu.img" :alt="currentMenu.title" />
                        <template v-if="currentMenu.cardLink">
                          <footer class="card-footer has-text-centered has-background-primary-lighter">
                            <a class="card-footer-item has-text-weight-bold">{{ currentMenu.cardLink }}</a>
                          </footer>
                        </template>
                      </div>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <br>
        <div id="newsandcommunity" class="columns is-variable is-6">
          <div v-for="card in cards" :key="card.title" class="column is-half">
            <div class="card card-fullheight">
              <header class="card-header has-background-success ">
                <p class="card-content has-text-weight-bold has-text-white">{{ card.title }}</p>
              </header>
              <div class="card-content has-text-justified">
                <table>
                  <template v-for="el in card.text">
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    <tr v-if="el.date">
                      <td>{{ el.date }}</td>
                      <td>
                        <router-link :to="{ name: 'about', hash: `#${el.hash}` }">
                          {{ el.text }}
                        </router-link>
                      </td>
                    </tr>
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    <tr v-else>
                      <span v-html="el.text"></span>
                    </tr>
                  </template>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { default as messages } from '../helpers/messages';

/* eslint-disable global-require */
export default {
  name: 'Home',
  data() {
    return {
      menu: [
        { title: 'Welcome',
          text: '<b>Metabolic Atlas</b> integrates open source genome-scale metabolic models (GEMs) of human and yeast for easy browsing and analysis. It also contains many more GEMs constructed by our organization.<br><br>Detailed biochemical information is provided for individual model components, such as reactions, metabolites, and genes. These components are also associated with standard identifiers, facilitating integration with external databases, such as the Human Protein Atlas. <br><br><a href="https://doi.org/10.1126/scisignal.aaz1482" target="_blank">Robinson, J., et al, 2020. <i>An atlas of human metabolism</i>. Sci. Signal. 13, eaaz1482 </a>',
          img: require('../assets/explorer.jpg'),
          cardLink: 'Explore a GEM',
          route: { name: 'explorerRoot' },
          icon: 'home' },
        { title: messages.gemBrowserName,
          text: 'The <b>GEM Browser</b> enables powerful query and exploration of model content in tabular format.<br><br>A wide range of attributes, including reaction equations, metabolite formulas, gene rules and subsystem contents, are presented as a detailed network of individual model components. They are highly interconnected and rationally associated to easily navigate and switch between them.<br><br>Visit the documentation to learn about the different functionalities provided by the GEM Browser.',
          img: require('../assets/gemBrowser.jpg'),
          cardLink: 'Explore Human-GEM with the GEM Browser',
          route: { name: 'browserRoot', params: { model: 'human1' } },
          icon: 'table' },
        { title: messages.mapViewerName,
          text: 'For easy visualization, <b>Metabolic Atlas</b> handles both 2D and 3D maps. For each of the integrated models, the website automatically generates 3D graphs at both compartment and subsystem level.<br><br>Both compartment and subsystem 2D maps of the Human-GEM have been created by the contributors to Human-GEM and are manually curated. On these maps, one can search for reactions, metabolites or genes. Moreover, RNA expression data from Human Protein Atlas can be overlaid.<br><br>By clicking on an element on the map, more information of that element will be shown on the left sidebar. From there, one can navigate back to the <b>GEM Browser</b> for detailed information.',
          img: require('../assets/mapViewer.jpg'),
          cardLink: 'Explore the Golgi apparatus with the Map Viewer',
          route: { name: 'viewer', params: { model: 'human1', type: 'compartment', map_id: 'golgi_apparatus' }, query: { dim: '2d' } },
          icon: 'map-o' },
        { title: messages.interPartName,
          text: `The <b>Interaction Partners</b> graph shows connectivity between metabolites and genes based on their associated reactions.<br><br>The graph is dynamically generated and is customizable. One can interact with a restricted part of the metabolic network, or further expand the interaction partners of any element already on the graph. Moreover, RNA expression data from the Human Protein Atlas can be overlaid onto the graph. <br><br>This feature is available only for metabolites and genes, and is accessible via the <b>${messages.gemBrowserName}</b>.`,
          img: require('../assets/interaction.jpg'),
          cardLink: 'View glyoxalate[p] in Interaction Partners',
          route: { name: 'interPartner', params: { model: 'human1', id: 'm02007p' } },
          icon: 'connectdevelop' },
        { title: 'Search',
          text: 'The menu bar contains a shortcut to the <b>Global search</b> function, which enables users to easily search cellular components across all the integrated models. Further filtering is also available, based on result type (e.g. metabolite) and its parameters (e.g. compartment).<br><br>For retrieving larger subsets of the model, we recommend experienced users to use our the API. Alternatively, models can be downloaded from the <b>GEM Repository</b> page or from their original repository on GitHub.<br><br>',
          img: require('../assets/search.jpg'),
          cardLink: 'Search within all integrated GEMs',
          route: { name: 'search', query: { term: '' } },
          icon: 'search' },
        { title: 'Analyze',
          text: 'Gene expression data from the Human Protein Atlas can be viewed in the 2D and 3D maps and Interaction Partners. User data can also be overlaid onto the maps, with the option of comparing datasets, for example against normal tissue.<br><br>Additional types of omics integrations are under development.',
          img: require('../assets/analyze.jpg'),
          route: '',
          icon: 'tasks' },
        { title: 'GEM Repository',
          text: 'Over 350 GEMs can be downloaded from the <b>GEM Repository</b> or directly from the <b>Metabolic Atlas FTP server</b>. The tabular view enables customized selection.<br><br>Clicking on each of the models brings up more information about the model, including a text description and, if available, references. For support, the original authors should be contacted.',
          img: require('../assets/gems.jpg'),
          cardLink: 'GEM Repository',
          route: { name: 'gems' },
          icon: 'files-o' },
        { title: 'Export',
          text: '<b>Metabolic Atlas</b> provides open access to the models and associated annotations. Most of the data provided on the website is convenient to export, for example via <b>Export to TSV</b> buttons.<br><br>For the ones interested in extracting data in JSON format, we have documented our API. When using images or files obtained from our website, use the following reference:<br><br><a href="https://doi.org/10.1126/scisignal.aaz1482" target="_blank">Robinson, J., et al, 2020. <i>An atlas of human metabolism</i>. Sci. Signal. 13, eaaz1482 </a>',
          img: require('../assets/export.jpg'),
          cardLink: 'Export TSV for glyoxolate metabolites',
          route: { name: 'search', query: { term: 'glyoxalate' } },
          icon: 'download' },
        { title: 'Resources',
          text: 'Working with metabolic models requires a set of tools and external databases, which we have collected together for one-click access.<br><br>Additionally, Metabolic Atlas is open to further integrations.',
          img: require('../assets/resources.jpg'),
          cardLink: 'Resources',
          route: { name: 'resources' },
          icon: 'gears' },
      ],
      currentMenu: {},
      cards: [
        { title: 'Latest news',
          text: [
            { date: '2020.04.27',
              hash: '27-April-2020',
              text: 'Metabolic Atlas v1.7 brings Map Viewer improvements' },
            { date: '2020.03.23',
              hash: '23-March-2020',
              text: 'Metabolic Atlas v1.6' },
            { date: '2020.02.07',
              hash: '7-February-2020',
              text: 'Metabolic Atlas v1.5 updates both integrated models' },
            { date: '2019.09.11',
              hash: '11-September-2019',
              text: 'Metabolic Atlas was presented in a course given by NBIS' },
            { date: '2019.09.05',
              hash: '5-September-2019',
              text: 'Metabolic Atlas v1.4 enables gene expression comparison' },
            { date: '2019.08.01',
              hash: '1-August-2019',
              text: 'Metabolic Atlas v1.3' },
            { date: '2019.06.25',
              hash: '25-June-2019',
              text: 'Metabolic Atlas is upgraded to v1.2 with Human1 updated to v1.1' },
            { date: '2019.05.29',
              hash: '29-May-2019',
              text: 'Metabolic Atlas is upgraded to v1.1' },
            { date: '2019.05.17',
              hash: '17-May-2019',
              text: 'Metabolic Atlas is publicly available as v1.0' },
          ],
        },
        { title: 'Community',
          text: [
            { text: '<p>We are grateful for the efforts of scientists all over the world in creating the knowledge required to assemble high quality genome scale metabolic models and are passionate about continuing on this journey of open curation of models.<br><br>We invite you to explore the world of GEMs through Metabolic Atlas, and hope it will enhance your interest in this field. We wish to continuously improve Metabolic Atlas for the community. Email us with any feedback, suggestions, or requests at <a href="mailto:">contact [at] metabolicatlas [dot] org</a>.</p>' },
          ],
        },
      ],
    };
  },
  beforeMount() {
    this.currentMenu = this.menu[0]; // eslint-disable-line prefer-destructuring
  },
};

</script>
<style lang="scss">
.hero-video video {
  @media only screen and (max-width: $desktop) {
    max-width: inherit;
  }
}

#home {
  #menu-desktop {
    outline: 1px solid $primary;
    li {
      &:first-child {
        margin-top: 0.75em;
      }
      &:last-child {
        margin-bottom: 0.75em;
      }
      a {
        color: $white-bis;
        padding-left: 0.5em;
        line-height: 2;
      }
      a:hover {
        color: $white-bis;
        background-color: $primary-light;
        border-radius: 0;
      }
      .is-active {
        color: $black;
        background-color: $white;
        border-radius: 0;
      }
    }
  }
  .is-hidden-touch .card .card {
    max-width: 480px;
  }
  #menu-mobile li {
    padding-top: 10px;
    a {
      color: $white-bis;
    }
    a:hover {
      background-color: $primary-light;
    }
    .is-active {
      color: $black;
      background-color: $white;
    }
  }
  .margin-fix {
    margin-top: 1rem;
    margin-bottom: 1rem;
    margin-left: 0;
  }
  .more-padding {
    @media only screen and (min-width: $desktop) {
      padding: 1.5rem 2rem 1.5rem 2rem;
    }
  }
  .card-header > .card-content {
    padding-top: 0.5em;
    padding-bottom: 0.5em;
  }
  .is-v-aligned {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .tabs ul {
    flex-shrink: 1;
    flex-wrap: wrap;
    border-bottom-color: transparent;
  }
}

#newsandcommunity {
  .card-header {
    outline: 1px solid $primary;
  }
  td:first-child {
    padding-right: 10px;
  }
}

</style>
