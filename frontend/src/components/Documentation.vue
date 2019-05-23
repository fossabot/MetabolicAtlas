<template>
  <section class="section section-no-top extended-section">
    <div class="container">
      <h2 class="title is-2">Documentation</h2>
      <br>
      <div class="columns is-variable is-8">
        <div class="column is-narrow">
          <aside class="menu">
            <p class="menu-label">
              Table of Contents
            </p>
            <ul class="menu-list">
              <li>
                <a href="#Explore"><b>Explore integrated models</b></a>
                <ul class="menu-list">
                  <li><a href="#GEM Browser">GEM Browser</a></li>
                  <ul class="menu-list">
                    <li><a href="#GEM Browser Search">Search</a></li>
                    <li><a href="#Interaction Partners">Interaction Partners</a></li>
                  </ul>
                  <li><a href="#Map Viewer">Map Viewer</a></li>
                  <ul class="menu-list">
                    <li><a href="#2D Viewer">2D Viewer</a></li>
                    <li><a href="#3D Viewer">3D Viewer</a></li>
                  </ul>
                  <li><a href="#HPA RNA levels">HPA RNA levels</a></li>
                  <li><a href="#API">API</a></li>
                  <li><a href="#Global search">Global search</a></li>
                </ul>
              </li>
              <li>
                <a href="#GEMs"><b>GEMs</b></a>
                <ul class="menu-list">
                  <li><a href="#Integrated models">Integrated models</a></li>
                  <li><a href="#Repository">Repository</a></li>
                  <li><a href="#Comparison">Comparison</a></li>
                  <li><a href="#FTP-download">FTP download</a></li>
                </ul>
              </li>
              <li><a href="#Resources"><b>Resources</b></a></li>
            </ul>
          </aside>
        </div>

        <div class="column content is-medium has-text-justified">
          <h3 id="Explore">Explore integrated models</h3>
          The <i>Explore</i> section of Metabolic Atlas allows to vizualize the content of the integrated <a href="#Integrated-models">Genome-scale metabolic models (GEMs)</a> by using the <a href="#GEM Browser">GEM browser</a> tool and allows to navigate the metabolic network maps via the <a href="#Map-Viewer">Map viewer</a> tool. These two tools are available once one of the integrated models have been selected. The selected model is indicated on the right side of the Metabolic Atlas's logo in the top navigation bar. Leaving the <i>Explore</i> section (or the <i>GEM Browser</i> / <i>Map Viewer</i> tools) will unselect the model, and remove its name from the navigation bar.<br>
          To browse our integrated genome-scale metabolic models, please refer to the <router-link :to="{ name: 'gems'}">GEM Repository</router-link> page.<br>
          The <i>GEM Browser</i> and the <i>Map Viewer</i> are closely connected, one can navigate between the two tools using the buttons in the navigation bar.

          <h4 id="GEM Browser">GEM Browser</h4>
          The <i>GEM Browser</i> is a set of dedicated pages for multiple metabolic components of the model; reaction, metabolite, enzyme/gene, subsystem, compartment.

          <h5>Reaction page</h5>
          This page shows information about the current selected reaction. If available, a list of references (PMIDs) is also shown in the Reference table below.<br>
          On the right of the page, a list of maps/networks where this reaction can be vizualize is displayed. Clicking on a map name will redirected the user to the <i>Map Viewer</i> tool, to come back to the <i>GEM Browser</i> click the <i>GEM Browser</i> button in the header bar.

          <h5>Metabolite page</h5>
          The Metabolite page shows information on the current selected metabolite. Metabolite compounds in GEMs are ofter distinct according their cell compartment localization (e.g., reticulum endoplasmic); for this reason, one biological metabolite, e.g., cholesterol, might correspond to several metabolites in GEMs such as cholesterol[c] or cholesterol[m] (the suffix indicates in which compartment the metabolic is localized).<br>
          The top table contains basic information extracted from the metabolic model. If provided, several additional identifiers from external databases will be shown in the External IDs table below.<br>
          On the right side of the page user can access the interaction partners [link] tool for this metabolite.

          <h6 class="has-text-grey">Reactions table</h6>
          Show all the reactions involving the current metabolite, either as a reactant or a product.<br> The current metabolite is denoted with a black text color in the reaction's equations.<br>
          Since a metabolite is restricted to a cell compartment, Only reactions involving metabolites in that compartment are displayed. To remove this restriction and display additional reactions, click the <i>Expand to all compartments</i> button.<br>
          <i>Please note</i> that the number of reactions is limited to 200; to get all the reactions we invite users to use the <a href="#API">API</a>.

          <h5>Enzyme page</h5>
          Show information on the current selected enzyme/gene. The top table contains basic information extracted with the metabolic model. If provided several, additional identifiers from external databases will be shown in the external IDs table.<br>On the right side of the page user can access the interact partners [link] for this enzyme/gene.

          <h6 class="has-text-grey">Reactions table</h6>
          Show all the reactions involving the current enzyme.<br>
          <i>Please note</i> that the number of reactions is limited to 200; to get all the reactions we invite users to use the <a href="#API">API</a>.

          <h5>Subsystem page</h5>
          This page shows information on the current selected subsystem. Subsystems correspond to a group of reactions playing a role in the same metabolic function. In GEMs, not all the reactions in a given subsystem have to be linked into a complete network, unlike reactions in a metabolic pathway.<br>
          The list of metabolites and enymes are shown in the table but restricted to 1000 for each category. Use the <a href="#API">API</a> to get them all for the selected subsystem.<br>

          <h6 class="has-text-grey">Reactions table</h6>
          Show all the reactions part of the current subsystem. In some GEMs a given reaction can be part of multiple subsystems.
          <i>Please note</i> that the number of reactions is limited to 1000; to get all the reactions we invite users to use our <a href="#API">API</a>.

          <h5>Compartment page</h5>
          Show information on the current selected compartment. The full list of metabolites, enzymes, reactions is available through the <a href="#API">API</a>.

          <h4 id="GEM Browser Search">Search</h4>
          Search for any term in metabolites, enzymes, reactions, subsystems or compartments information.<br>
          The search is restricted to the selected model and limited to 50 results per type. Alternatively, you can press Enter run the query on the <i>Global Search</i>, where the term is search against all the integrated model's component and unrestricted. To learn more about the search terms possiblities go to the <a href="#Global Search">Global Search</a> section of this page.

          <h4 id="Interaction Partners">Interaction Partners</h4>
          For a given metabolite or enzyme, this page shows the other metabolites and enzymes that interact with it. The selected metabolite or enzyme is centered on the graph. Connectivity is computed from chemical equations that involve this metabolite or enzyme. For medium size networks of interaction partners, the user is asked to generate the graph. For very large network (e.g. with H<sub>2</sub>O) the graph will not be generated. Users can click on a node to display a context menu with 3 options:<br>
          <ul>
            <li>Load interaction partners: reload the interactions partners graph with the clicked node as central node</li>
            <li>Expand interaction partners: add additionnal interactions partners nodes of the clicked node to the graph. Expanded interactions are represented as dotted lines.</li>
            <li>Highlight reaction: each nodes might be involve in many chemical reactions. Select a reaction from the list to show the others interaction partners in the scope of the selected reaction (others interaction partners will be grayed-out). The hightligthed reaction ID will be show on the top of the graph. The directionality of each edge is indicated as triangle, or diamonds in case of for reversible reaction. To remove the highlight click on the "eraser" button on the top of the graph.</li>
          </ul>
          Clicking on a node also shows a link on the right sidebar to quickly access the <a href="#GEM Browser">GEM browser</a> page of that node.
          The top-left buttons allow to (from left to right): customize the graph node's shape and colors, zoom-in, zoom-out, reset the display, reload graph (removes expanded interaction partners), and hide any reaction highlight. The nodes can also be moved around on the graph.

          <h6 class="has-text-grey">Export graph</h6>
          Clicking the <i>Export graph</i> button, two options are displayed: GraphML or PNG. The first is a Cytoscape compatible GraphML format; currently the colors are not exported in this format.

          <h6 class="has-text-grey">Highlights</h6>
          Nodes might belong to multiple compartments / subsystems. The filter box allows to highlight (red text color) the node in a given subsystem or compartment. The two filters are additive, and can be clear using the erase button.

          <h6 class="has-text-grey">Nodes table</h6>
          All the metabolites and enzyme nodes are shown in this table, along with their compartment localization. For enzymes, the compartment is computed using the localization of the metabolites of reactions catalyzed by said enzyme; it does not describe the <i>in vivo</i> localization of the enzyme in the cell compartment. Selecting a row will select the node on the graph and vice versa, selecting a node on the graph will select the row in the table. The search bar above the table can be used to filter out rows to find a given component.

          <h4 id="Map Viewer">Map Viewer</h4>
          The <i>Map Viewer</i> is a separated and independant interface, accessible after an integrated model has been selected. It includes a 2D viewer to vizualize metabolic maps in SVG format, and a 3D viewer to look at the metabolic network in 3 dimensional space. Users can easly toggle between <i>GEM Browser</i> and <i>Map Viewer</i> using the header buttons.<br>
          To switch between 2D maps and 3D network use the top left button. This button is disabled for model without 2D maps or when the alternative 2D version of a 3D maps is not available [refactor]. To select a compartment or subssystem use the 2 left sidebar buttons.

          <h5 id="2D Viewer">2D Viewer</h5>
          2D SVG maps are provided with metabolic models. They represented either a cell compartment or a subsystem/pathway. While a very high percentage of the reactions in the model are represented on the 2D maps, some can still be missing.<br>
          3 buttons on the top left of the UI allow to Zoom in, Zoom out and Show/Hide the genes/enzymes on the loaded map respectively.<br>
          Users can interact with the maps using the mouse by clicking and dragging the mouse to pan the view and using the wheel button to zoom in/out.<br>
          A search function is available for 2D maps using the search bar. The window will zoom and center on hits found. Click the 'highlight' button to color in red all the hits on the maps. To remove the highlight, simply empty the search bar.<br>
          SVG are interactive; click on a node (metabolite, reaction, enzyme) or a subsystem to load some of its information in the sidebar. Additonal information of the corresponding selected element is shown by clicking the <i>GEM browser</i> button.<br>

          <h5 id="3D Viewer">3D Viewer</h5>
          3D renderings of the metabolic network are automatically generated from the model data. This 3D graph contains all the reactions in the model.<br>
          Interaction on the 3D graph is possible using the mouse by holding left-click and move the mose to rotate the view, right-click to pan, and use the mouse wheel to zoom in/out.<br>
          Users can also hover a node to overlay its the name/id orleft-clik on a node (wait for the graph to be completly static) to display some of its information in the sidebar. Additonal information of the corresponding selected element is shown by clicking the <i>GEM browser</i> button.<br>

          <h5 id="HPA RNA levels">Human Protein Atlas RNA levels</h5>
          RNA expressinon levels for enzymes, provided by the Human Protein Atlas, can be loaded using the corresponding sidebar button. Once selected, the RNA tissue will be applied to the selected map. To clear RNA level, use the <i>Clear selection</i> button. RNA levels are available for both the 2D and 3D viewers.<br>
          Expression levels from the Human Protein Atlas can be loaded in the <i>Interaction Partners</i> using the panel on the right, and in the <i>Map Viewer</i> using the corresponding sidebar button. Doing so will update the enzyme node's color only according to the legend. Some enzymes might not have RNA levels, in such case their color corresponds to the n/a color.
          <div v-html="getExpLvlLegend()"></div><br>

          <h3 id="Global search">Global search</h3>
          The <i>Global search</i> page queries all the integrated metabolic models. Each metabolic component has its own results table accessible via the dedicated tab. Tabs are inactivated when no results are found. Search criteria are not restricted to the columns, for instance searching for an MNXref ID will output results for the metabolite or reactions matching the ID. The search algorithm matches partial name of component: searching for 'choleste' will output all metaboties containing the substring cholesterol. When the complete name of a metabolite is provide. e.g. 'cholesterol' not only all the metabolite matching or partially matching this name is provided, but the list of reaction that involve the 'cholesterol' metabolite is pull out from the database. The global search is also able to query reactions in a more advance way using special keyword:<br>
            - use " => " and metabolite terms - ID (m02439c), name (malate) or full name (malate[c]) - in the query term to indicate the algorithm you are looking for a reactions only, and a reaction that involve a specify metabolites as reactant/product.<br>

          <h3 id="API">API</h3>
          We have a dedicated interface to facilite the use of the API, with output provided in JSON format. The API is still under developpement and subject to change without notice.

          <h3 id="GEMs">GEMs</h3>
          A genome scale metabolic model (GEM) is a mathematical representation of a metabolic network.

          <h4 id="Integrated models">Integrated GEMs</h4>
          Currently Metabolic Atlas contains two integrated models, yeastGEM and humanGEM.

          <h4 id="Repository">Repository</h4>
          Currently, the Repository lists all models made by the SysBio research group; this includes older models that might no longer be maintained (for example HMR2), but also those just published. The later ones can also be found in the SysBioChalmers organization on GitHub.<br>
          Click on a row on the table to show more information about this GEM. Users can download models in various file format (when available).

          <h4 id="Comparison">Comparison</h4>
          Currently, the <i>Comparison</i> page provides statistics about the comparison/overlap between Human1 and HMR2, and Recond3D.

          <h4 id="FTP-download">FTP download</h4>
          Genome-Scale Metabolic model files can be downloaded from <a href="https://ftp.metabolicatlas.org">ftp.metabolicatlas.org</a> or by connecting to the FTP using your favorite FTP client (e.g. <a href="https://filezilla-project.org/">FileZilla</a>).

          <br>
          <span class="has-text-weight-bold lab">Host:</span> <a href="https://ftp.metabolicatlas.org">ftp.metabolicatlas.org</a><br>
          <span class="has-text-weight-bold lab">Login:</span> (leave it empty)<br>
          <span class="has-text-weight-bold lab">Password:</span> (leave it empty)<br>
          <span class="has-text-weight-bold lab">Port:</span> 21

          <h3 id="Resources">Resources</h3>
          This is a list of the most relevant software tools, algorithms or databases published by the SysBio group. To navigate to the cprresponding pages, click o the image on the left.

        </div>
      </div>
    </div>
  </section>
</template>

<script>

import $ from 'jquery';
import { getExpLvlLegend } from '../expression-sources/hpa';

export default {
  name: 'help',
  mounted() {
    if (this.$route.hash) {
      $(window).scrollTop($(this.$route.hash).offset().top);
    }
  },
  methods: {
    getExpLvlLegend,
  },
};
</script>

<style lang="scss"></style>
