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
                <a href="#GEM Browser"><b>GEM Browser</b></a>
                <ul class="menu-list">
                  <li><a href="#GEM Browser Search">Search</a></li>
                  <li><a href="#Interaction Partners">Interaction Partners</a></li>
                </ul>
                <a href="#Map Viewer"><b>Map Viewer</b></a>
                <ul class="menu-list">
                  <li><a href="#2D Viewer">2D Viewer</a></li>
                  <li><a href="#3D Viewer">3D Viewer</a></li>
                </ul>
              </li>
              <a href="#HPA RNA levels"><b>RNA levels</b></a>
              <a href="#Global-search"><b>Global search</b></a>
              <li>
                <a href="#GEMs"><b>GEMs</b></a>
                <ul class="menu-list">
                  <li><a href="#Integrated models">Integrated models</a></li>
                  <li><a href="#Repository">Repository</a></li>
                  <li><a href="#Comparison">Comparison</a></li>
                  <li><a href="#FTP-download">FTP download</a></li>
                </ul>
              </li>
              <li>
                <a href="#Resources"><b>Resources</b></a>
                <ul class="menu-list">
                  <li><a href="#API">API</a></li>
                </ul>
              </li>
            </ul>
          </aside>
        </div>
        <div id="documentation" class="column content is-medium has-text-justified">
          Metabolic Atlas allows users to vizualize the content of the integrated <a href="#Integrated-models">Genome-scale metabolic models (GEMs)</a> by using the <a href="#GEM Browser">GEM browser</a> tool, and enables navigation of the metabolic network maps via the <a href="#Map-Viewer">Map viewer</a> tool. These two tools are available upon selecting one of the integrated models. The selected model is indicated to the right of the Metabolic Atlas logo in the top navigation bar. Leaving the <i>Explore</i> section (or the <i>GEM Browser</i> / <i>Map Viewer</i> tools) will unselect the model, and remove its name from the navigation bar.<br>
          To browse our integrated GEMs, visit the <router-link :to="{ name: 'gems'}">GEM Repository</router-link> page.<br>
          The <i>GEM Browser</i> and the <i>Map Viewer</i> are closely connected, and users can navigate between the two tools using the buttons in the top navigation bar.

          <hr>
          <h3 id="GEM Browser">GEM Browser</h3>
          The <i>GEM Browser</i> is a set of dedicated pages for different components of the model; reactions, metabolites, enzymes/genes, subsystems, and compartments.

          <h5>Reaction page</h5>
          This page shows information about the current selected reaction. If available, a list of references (PMIDs) is also shown in the Reference table below.<br>
          On the right of the page, a list of maps/networks where this reaction can be vizualize is displayed. Clicking on a map name will redirect the user to the <i>Map Viewer</i> tool; to return back to the <i>GEM Browser</i>, click the <i>GEM Browser</i> button in the top navigation bar.

          <h5>Metabolite page</h5>
          The Metabolite page shows information on the current selected metabolite. Metabolites in GEMs are often differentiated according to their cell compartment localization (e.g., endoplasmic reticulum). For this reason, one metabolic species, e.g. cholesterol, may correspond to several different metabolite entries in a GEM, such as cholesterol[c], cholesterol[m], etc. (the suffix indicates the compartment in which the metabolite is localized).<br>
          The top table contains basic information extracted from the GEM. If provided, several additional identifiers from external databases will be shown in the External IDs table below.<br>
          On the right side of the page, users can access the <a href="#Interaction Partners">Interaction Partners</a> tool for the metabolite.

          <h6 class="has-text-grey">Reactions table</h6>
          Lists all the reactions involving the current metabolite as a reactant or a product. The current metabolite is denoted with a black text color in the reaction equations. Since metabolites are specific to a cell compartment, only reactions involving the metabolite in its specific compartment are displayed. To remove this restriction and display additional reactions involving the metabolite in any compartment, click the <i>Expand to all compartments</i> button.<br>
          Note that the number of reactions is limited to 200; to retrieve all the reactions we invite users to use the <a href="#API">API</a>.

          <h5>Enzyme page</h5>
          Shows information about the current selected enzyme/gene. The top table contains basic information extracted from the GEM. If provided, several additional identifiers from external databases will be shown in the external IDs table.<br>On the right side of the page, users can access the <a href="#Interaction Partners">Interaction Partners</a> tool for this enzyme/gene.

          <h6 class="has-text-grey">Reactions table</h6>
          Lists all the reactions catalyzed by the current enzyme.<br>
          Note that the number of reactions is limited to 200; to retrieve all the reactions we invite users to use the <a href="#API">API</a>.

          <h5>Subsystem page</h5>
          This page shows information on the current selected metabolic subsystem. Subsystems correspond to a set of reactions that share a similar metabolic function. Unlike a metabolic pathway, the reactions comprising a subsystem are not necessarily linked into a completely connected network.<br>
          A list of metabolites and enzymes contained within the current subsystem are shown in the table, but are restricted to a maximum of 1000 for each category. Use the <a href="#API">API</a> to retrieve the complete set of metabolites and enzymes for the selected subsystem.<br>

          <h6 class="has-text-grey">Reactions table</h6>
          Shows all the reactions that belong to the current subsystem. Note that in some GEMs, a given reaction can be associated with multiple subsystems.
          The number of reactions shown is limited to 1000; to retrieve all associated reactions we invite users to use the <a href="#API">API</a>.

          <h5>Compartment page</h5>
          Shows information on the current selected compartment. The full list of metabolites, enzymes and reactions is available through the <a href="#API">API</a>.

          <h5 id="GEM Browser Search">Search</h5>
          Search for any term in metabolites, enzymes, reactions, subsystems, or compartments information.<br>
          The search is restricted to the selected GEM and limited to 50 results per type. Alternatively, users can click on the banner under the search input field to run a <i>Global Search</i>, where the term is searched among all the integrated models' components and is unrestricted. To learn more about the search term possiblities, go to the <a href="#Global Search">Global Search</a> section of this page.

          <h5 id="Interaction Partners">Interaction Partners</h5>
          For a given metabolite or enzyme, this page shows the other metabolites and enzymes with which it interacts via shared reaction(s). The selected metabolite or enzyme is centered on the graph. Connectivity is computed from reaction equations that involve this metabolite or enzyme. For medium-sized networks of interaction partners, the user is prompted before generating the graph. For very large networks (e.g. for H<sub>2</sub>O) the graph will not be generated. Users can click on a node to display a context menu with 3 options:<br>
          <ul>
            <li>Load interaction partners: reload the interaction partners graph with the clicked node as the new central node.</li>
            <li>Expand interaction partners: add additional interaction partner nodes for the clicked node to the graph. Expanded interactions are represented with dashed lines.</li>
            <li>Highlight reaction: some nodes may be involve in many different reactions. Select a reaction from the list to show the other interaction partners associated with the selected reaction (other interaction partners will be grayed-out). The directionality of each edge is indicated as a triangle, or diamonds in case of a reversible reaction. To remove the highlight, click on the "eraser" button at the top of the graph.</li>
          </ul>
          Clicking on a node also shows a link on the right sidebar to quickly access the <a href="#GEM Browser">GEM browser</a> page for that node.
          The top-left buttons allow users to (from left to right): customize the graph node's shape and colors, zoom in, zoom out, reset the display, reload the graph (remove expanded interaction partners), and remove any highlighting. The nodes can also be moved around the graph by the user.

          <h6 class="has-text-grey">Export graph</h6>
          Clicking the <i>Export graph</i> button will display two options: GraphML or PNG. The first is a Cytoscape compatible GraphML format; currently, the colors are not exported in this format.

          <h6 class="has-text-grey">Highlights</h6>
          Nodes may belong to multiple compartments and/or subsystems. The filter box allows users to highlight (label color) the nodes belonging to a given subsystem or compartment. The two filters are additive. Enzymes may catalyze multiple reactions in differents compartments / subsystems - such enzymes are highlighted in orange.

          <h6 class="has-text-grey">Reactions table</h6>
          Information of the reactions are listed in this table. Selecting a label of metabolite or enzyme in the table will select the corresponding node on the graph, and vice versa. Selecting a reaction ID label highlight the reaction on the graph. The search bar above the table can be used to filter out rows to find a given component. The table can be exported via the "Export to TSV" button.

          <hr>
          <h3 id="Map Viewer">Map Viewer</h3>
          The <i>Map Viewer</i> is a separate and independent interface, accessible after an integrated model has been selected. It includes a 2D viewer to vizualize metabolic maps in SVG format, and a 3D viewer to explore the metabolic network in 3 dimensions. Users can easly toggle between the <i>GEM Browser</i> and <i>Map Viewer</i> using the buttons in the top navigation bar.<br>
          To switch between 2D maps and 3D network, use the "Switch to 2D" or "Switch to 3D" button in the top left of the map, respectively. This button is disabled for a model without 2D maps, or when the corresponding 2D version of a 3D network is not available. The two left sidebar buttons are used to select which compartment or subsystem will be shown in the viewer.

          <h5 id="2D Viewer">2D Viewer</h5>
          2D SVG maps are provided for integrated GEMs. They represent either a cell compartment or a subsystem/pathway. While a very high percentage of the reactions in the model are represented on the 2D maps, some may be unavailable.<br>
          Three buttons on the top left of the UI allow users to zoom in, zoom out and show/hide the genes/enzymes on the current map.<br>
          Users can interact with the maps by clicking and dragging the mouse to pan the view or using the mouse wheel to zoom in/out.<br>
          A search function is available for 2D maps using the search bar. The window will zoom and center on each component found. Click the 'highlight' button to color all found components on the maps in red. To remove the highlight, simply clear the search bar.<br>
          The SVGs are interactive; click on a node (metabolite, reaction, enzyme) or a subsystem to load some of its information in the sidebar. Additonal information on the corresponding selected element can be accessed by clicking the <i>GEM browser</i> button.<br>

          <h5 id="3D Viewer">3D Viewer</h5>
          3D renderings of the metabolic network are automatically generated from the GEM data. This 3D graph contains all the reactions in the model, grouped by cellular compartment or subsystem.<br>
          Interaction with the 3D graph is possible using the mouse by holding left-click and moving the mose to rotate the view, right-click to pan, and use the mouse wheel to zoom in/out.<br>
          Users can also hover a node to view its name/id or left-clik on a node (once the graph has stopped moving) to display some of its information in the sidebar. Additonal information on the corresponding selected element can be accessed by clicking the <i>GEM browser</i> button.<br>

          <hr>
          <h3 id="HPA RNA levels">RNA levels</h3>
          <div class="columns is-marginless">
            <div class="column is-paddingless">
            RNA expression levels for enzymes from <a href="http://proteinatlas.org" target="_blank">The Human Protein Atlas</a> can be loaded using the corresponding sidebar button. Once selected, the RNA levels corresponding to the chosen tissue will be overlaid on the selected map. To clear the RNA levels, use the <i>Clear selection</i> button. RNA levels are available for both the 2D and 3D viewers.<br>
            Expression levels from the Human Protein Atlas can be loaded in the <i>Interaction Partners</i> graph using the panel on the right, and in the <i>Map Viewer</i> using the corresponding sidebar button. Doing so will update the enzyme's node color according to the legend. Some enzymes may not have RNA levels available - in such case their color corresponds to the n/a color.
            </div>
            <div class="column" v-html="getExpLvlLegend()" style="padding-right: 0">
            </div>
          </div>

          <hr>
          <h3 id="Global-search">Global search</h3>
          The <i>Global search</i> page queries all the integrated metabolic models. Each metabolic component has its own results table accessible via the dedicated tab. Tabs are inactivated when no results are found. The search text is not restricted to the visible columns; for example, searching an MNXref ID will return results for the metabolites and/or reactions matching the ID even though the MNXref column is not in the table. The search algorithm matches partial names of components: searching for 'cholesterol' will output all metabolites containing the substring 'cholesterol'. When the name of a metabolite is provided, all metabolites matching or partially matching this name be returned, in addition to a the list of all reactions that involve these matching metabolites. The global search is also able to query reactions in a more advanced way using special patterns:
          <ul>
            <li>Use the compartment letter at the end of a metabolite name, e.g cholesterol[c] to match metabolites associated with that compartment.</li>
            <li>Use " => " and metabolite terms - ID (m02439c), name (malate) or name with compartment (malate[c]) - in the query term to indicate that only reactions should be searched, and to return reactions involve the specified metabolite(s) as reactant/product. For example, "pyruvate =>" will return all reactions in which pyruvate participates as a reactant.</li>
            <li>Use " + " and metabolite terms - ID (m02439c), name (malate) or name with compartment (malate[c]) - to force the presence of multiple metabolites in the retrieved reactions. For example, "pyruvate + malate" returns all reactions involving at least pyruvate <b>and</b> malate.</li>
            <li>Combine the three patterns to refine the results even further.</li>
          </ul>

          <hr>
          <h3 id="GEMs">GEMs</h3>
          A genome-scale metabolic model (GEM) is a mathematical representation of a metabolic reaction network.

          <h5 id="Integrated models">Integrated GEMs</h5>
          Currently, Metabolic Atlas contains two integrated models, <i>YeastGEM</i> and <i>HumanGEM</i>.

          <h5 id="Repository">Repository</h5>
          The Repository lists all models constructed by the SysBio research group; this includes older models that may no longer be maintained (for example HMR2), and others that were recently published. The more recent GEMs can also be found in the <a href="https://www.github.com/SysBioChalmers/" target="_blank">SysBioChalmers organization GitHub</a>.<br>
          Click on a row in the table to show more information about a GEM. Users can download models in various file formats (when available).

          <h5 id="Comparison">Comparison</h5>
          The <i>Comparison</i> page provides statistics about the comparison/overlap between Human1 and HMR2, and Recond3D.

          <h5 id="FTP-download">FTP download</h5>
          Genome-Scale Metabolic model files can be downloaded from <a href="https://ftp.metabolicatlas.org">ftp.metabolicatlas.org</a> or by connecting to the FTP using your favorite FTP client (e.g. <a href="https://filezilla-project.org/">FileZilla</a>).

          <br>
          <span class="has-text-weight-bold lab">Host:</span> <a href="https://ftp.metabolicatlas.org">ftp.metabolicatlas.org</a><br>
          <span class="has-text-weight-bold lab">Login:</span> (leave it empty)<br>
          <span class="has-text-weight-bold lab">Password:</span> (leave it empty)<br>
          <span class="has-text-weight-bold lab">Port:</span> 21

          <hr>
          <h3 id="Resources">Resources</h3>
          Lists of the most relevant software tools, algorithms, or databases published by the SysBio group. To navigate to the corresponding pages, click on the image on the left of its description.

          <h5 id="API">API</h5>
          We have a dedicated interface to facilite the use of the API, with output provided in JSON format. The API is still under developpement and subject to change without notice.
        </div>
      </div>
    </div>
  </section>
</template>

<script>

import { getExpLvlLegend } from '../expression-sources/hpa';

export default {
  name: 'help',
  methods: {
    getExpLvlLegend,
  },
};
</script>

<style lang="scss"></style>
