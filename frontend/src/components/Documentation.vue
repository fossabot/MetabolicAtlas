<template>
  <section class="section extended-section">
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
                  <li><a href="#API">API</a></li>
                  <li><a href="#Global search">Global search</a></li>
                </ul>
              </li>
              <li>
                <a href="#GEMs"><b>GEMs</b></a>
                <ul class="menu-list">
                  <li><a href="#Repository">Repository</a></li>
                  <li><a href="#Comparison">Comparison</a></li>
                  <li><a href="#FTP download">FTP download</a></li>
                </ul>
              </li>
              <li><a href="#Resources"><b>Resources</b></a></li>
              <li><a href="#Privacy"><b>Privacy statement</b></a></li>
            </ul>
          </aside>
        </div>

        <div class="column content is-medium has-text-justified">
          <h3 id="Explore">Explore integrated models</h3>
          The explore section of metabolic Atlas allows to vizualize the content of the integrated Genome-scale metabolic models (GEMs) [link to gems section] by using the GEM browser [link] tool and allows to navigate the metabolic maps thanks to the Map viewer [link] tool. These two tools are available once one of the integrated models have been selected. The selected model is indicated on the right side of the metabolic Atlas's logo in the Header bar. Leaving the explore section (or the GEM browser / map viewer tools) will unselect the model, thus remove its name from the header bar.
          To browse our integrated genome-scale metabolic models, please refer to the <router-link :to="{ name: 'gems'}">GEMs Repository</router-link> page.
          [The GEM Browser and the Map viewer are closely connected, one can navigate between the two tools using the buttons in the header bar.]

          <h4 id="GEM-Browser">GEM Browser</h4>
          [intro for the GEM browser]
          The GEM browser is a series of dedicated pages for multiple metabolic components of the model; Reaction, metabolite, enzyme/gene, subsystem/pathway, compartment.
           <!-- ================ -->
          <h5 id="">Reaction page</h5>
          Show information on the current selected reaction. If available a list of references (PMIDs) is also show in the reference table.<br>
          On the right of the page, is displayed the list of maps/networks where this reaction can be vizualize. Clicking on a map name will redirected the user to the Map viewer tool, to come back to the GEM browser click the <i>GEM browser</i> button in the header bar.
          <!-- ================ -->
          <h5 id="">Metabolite page</h5>
          Show information on the current selected metabolite. Metabolite compounds in GEMs are ofter distinct according their cell compartment localization (e.g., reticulum endoplasmic), for this reason the one biological metabolite, e.g., cholesterol, might corresponds to severale metabolites in GEMs such as cholesterol[c] or cholesterol[m] (the suffix indicates in which compartment the metabolic is localized).
          The top table contains basic information extracted with the metabolic model. If provided several, additional identifiers from external databases will be shown in the external IDs table.<br>
          On the right side of the page user can access the interaction partners [link] tool for this metabolite.

          <h6 id="">Reactions table</h6>
          Show all the reactions involving the current metabolite, either as a reactant or a product.<br> The current metabolite is denoted with a black text color in the reaction's equations.
          Since a metabolite is restricted to a cell compartment, Only reactions involving metabolites in that compartment are displayed. To remove this restriction and display additional reactions, click the <i>Expand to all compartments</i> button.<br>

          <i>Please note</i> that the number of reactions will be limited to 200, to get all the reactions we invite users to use the API [link].
          <!-- ================ -->
          <h5 id="">Enzyme page</h5>
          Show information on the current selected enzyme/gene. The top table contains basic information extracted with the metabolic model. If provided several, additional identifiers from external databases will be shown in the external IDs table.<br>On the right side of the page user can access the interact partners [link] for this enzyme/gene.

          <h6 id="">Reactions table</h6>
          Show all the reactions involving the current enzyme.
          <i>Please note</i> that the number of reactions will be limited to 200, to get all the reactions we invite users to use the API [link].
          <!-- ================ -->
          <h5 id="">Subsystem page</h5>
          Show information on the current selected subsystem. Subsystems corresponds to a group of reactions playing a role in the same metabolic function. In GEMs all the reactions in a given subsystem might not be linked into a complete network as oppose what a metabolic pathway is [reformulate].
          The list of metabolites and enymes are show in the table but restricted to 1000 for each category. Use the API [link] to get them all for the selected subsystem.<br>

          <h6 id="">Reactions table</h6>
          Show all the reactions part of the current subsystem. In some GEMs a given reaction can be part of multiple subsystems.
          <i>Please note</i> that the number of reactions will be limited to 1000, to get all the reactions we invite users to use our API [link].
          <!-- ================ -->
          <h5 id="">Compartment page</h5>
          Show information on the current selected compartment. The full list of metabolites, enzymes, reactions is available through the API.

          <h4 id="GEM Browser Search">Search</h4>
          Search for the term in metabolites, enzymes, reactions, subsystems or compartments information.<br> The search is restricted to the selected model and limited to 50 results per type.<i>alternatively</i> you can press Enter run the query on the global search [link], where the term is search against all the integrated model's component and unrestricted. To learn more about the search terms possiblities go to the global seach section [link].
          <!-- ================ -->
          <h4 id="Interaction Partners">Interaction Partners (IPs)</h4>
          Show for a given metabolite or enyzyne the other metabolites and enzymes interacting with it. The selected metabolite of enzyme is centered on the graph. Connectivities are computed from chemical equations that involve this metabolite or enzyme, thus it does not consider, for enzyme, physical interaction into protein complexes. For medium size interaction parners network the user is asked to generate the graph, for very large network (e.g. with H2O) the graph will not be generated. Users can click on a node to display a context menu with 3 options:<br>
          <ul>
            <li>Load interaction partners: reload the interactions partners graph with the clicked node as central node</li>
            <li>Expand interaction partners: add additionnal interactions partners nodes, for the clicked, on the current graph. Expanded interactions are represented as dotted lines</li>
            <li>Highlight reaction: each nodes might be involve in many chemical reactions. Select a reaction from the list to show the others interaction partners in the scope of the selected reaction (others IPs will be grayed-out). The hightligthed reaction ID will be show on the top of the graph. The directionality of each edge is indicated as triangle, or diamonds in case of for reversible reaction. To remove the highlight click on the "eraser" button on the top of the graph.</li>
          </ul>
          Clicking on a node also show a link on the right sidebar to access quickly the GEM browser [link] page of that node.
          The top-left buttons allow to (from left to right): customize the graph node's shape and colors, zoom-in, zoom-out, reset the display, reload graph (clean remove expanded interaction partners), and hide any reaction highlight respectivly [add messsage on buttons on mouse over]. Nodes can be moved prior selection[reformulate].

          <h6 id="">Export graph</h6>
          Click the <b>Export graph</b> button, and you will be presented with two options: GraphML or PNG. The first is a Cytoscape compatible GraphML format, currently the colors are not exported in this format.

          <h6 id="">Expression levels</h6>
          Expression levels from the human protein atlas (HPA) can ge activate on the right panel, doing so will update the enzyme node's color only according to the the legend. Some enzymes might not have RNA lvl, in such case their color corresponds to the NA color.
          <div id="" v-html="getExpLvlLegend()"></div><br>

          <h6 id="">Highlights</h6>
          Nodes might belong to multiple compartment / subsystem at once. the filter box allows to hightlight (red text color) the node in a given subsystem or compartment. The two filters are additive, and can be clear using the erase button.

          <h6 id="">Nodes table</h6>
          All the metabolites and enzyme graph are shown in this table, along their compartment localization. For enzyme the compartment is computed using the localization of reactant and product metabolites of reactions catalyzed by the enzyme, it does not describe the in vivo localization of the enzyme in the cell compartment. Selecting a row will select the node on the graph and vice versa, selecting a node on the graph will select the row in the table. The search bar above the table can be use to filter out rows to find a given component.
          <!-- ================ -->
          <h4 id="Map Viewer">Map Viewer</h4>
          The Map viewer is a separated and independant interface, accessible when an integrated model has been selected. It includes a 2D viewer, to vizualize metabolic map in SVG format, and a 3D viewer, to look a the metabolic network on a 3 dimentional space. User can easly [jump back/switch between] on the GEM browser using the header button. To switch between 2D maps and 3D network use the top left buttons. This buttons is disabled for model without 2D maps or when a the alternative 2D version of a 3D maps is not available [refactor]. To select a maps compartment or subssystem use the 2 top sidebar buttons: 

          <h5 id="2D Viewer">2D Viewer</h5>
          2D SVG maps are provided with a metabolic models, They represented either a cell compartment or a subsystem/pathways. They is not garanty that all the reactions in the model are represented on the 2D maps.

          3 buttons on the top left of the UI allow to Zoom in, Zoom out and show/hide the genes/enzymes on the loaded map respectivly. 
          User can interaction with the maps using the mouse:
          - click and drag the mouse to pan the view
          - use the wheel button to zoom in/out.

          A search function is available for 2D maps using the search bar. The window will zoom and center on hits found. Click the 'highlight' button to redcolor all the hits on the maps. To remove the highlight simply empty the search bar.

          SVG are interactive; click on a node (metabolite, reaction, enzyme) or a subsystem to load some of its information in the sidebar. Users can then view additonal information of the corresponding selected element on the GEM browser by clicking the "GEM browser" button.
          Currently 2D SVG metabolic maps are only available for the humanGEM model.

          <h5 id="3D Viewer">3D Viewer</h5>
          3D network are automatically generated from the model data and connectivity. 3D graph contains all the reactions in the select models.

          Interaction on the 3D graph is possible using the mouse: 
          - hold left-click and move the mose to rotate the view
          - right-click to pan and use the mouse wheel to zoom in/out. 

          User can also hover a node to overlay its the name/id orleft-clik on a node (wait for the graph to be completly static) to display some of its information in the sidebar.  Users can then....

          <h5 id="HPA RNA LVL">Human Protein Atlas RNA levels</h5>
          RNA expressinon levels, provided by protein atlas, for enzymes can be loaded using the corresponding sidebar button. Once selected a RNA tissue will be apply to subsequent map selected, clear RNA lvl by using the clear selection button. RNA levels are available for both the 2D and 3D viewer.

          <!-- ================ -->
          <h3 id="Global search">Global search</h3>
          The global search inquiry in all the integrated metabolic models. Each metabolic components have its own results tables (inactivated when no hits are found) accessible via the dedicated tab. Search criteria are not restricted to the columns, for instance searching for an MNXref ID will output results for the metabolite or reactions matching the ID. The search algorithm match partial name of component: searching for 'choleste' will output all metaboties containing the substring cholesterol. When the complete name of a metabolite is provide. e.g. 'cholesterol' not only all the metabolite matching or partially matching this name is provided, but the list of reaction that involve the 'cholesterol' metabolite is pull out from the database. The global search is also able to query reactions in a more advance way using special keyword:
            - use " => " and metabolite terms - ID (m02439c), name (malate) or full name (malate[c]) - in the query term to indicate the algorithm you are looking for a reactions only, and a reaction that involve a specify metabolites as reactant/product. For instance to get the reactions that involve ATP as reactant and produce cholesterol in mitochondria

          If you for instance searched for ATP and then pressed Enter you will see that there are 11 metabolites that match this search term because sATP is found in 8 compartments, and dATP in 3.<br>
          In addition 11 enzymes match ATP, because there are whole families of ATP-related proteins.<br>
          In addition 739 reactions use, or produce ATP.<br>
          Click on the ID in order to be taken to the corresponding page.<br>
          On this page you also have the option of searching, but here it will instead search in the entire data, eg <i>across GEMs</i>.
          <!-- ================ -->
          <h3 id="API">API</h3>
          We have a dedicated interface to facilite the use of the API. JSON format are provided are output. The API is still under developpement and subject to change without notive. Changes will be though documented and highlight in the news section.
          <!-- ================ -->
          <h3 id="GEMs">GEMs</h3>
          [explain Genome-scale metabolic models (GEMs)]
          <h4 id="Integrated models">Integrated GEMs</h4>
          Currently Metabolic Atlas contains two integrated models, yeastGEM and humanGEM, both reconstructed by the group.
          <h4 id="Repository">Repository</h4>
          List all models made by the sysbio research group, this includes older models that might no longer be maintained (for example HMR2), but also those just published.
          The later ones can also be found in the SysbioOrganization (link) on github.<br>
          Click on a row on the table to show more information about this GEM. Users can download models in various file format (when available).

          <h4 id="Comparison">Comparison</h4>
          [Coming for the next release]
          <h4 id="FTP download">FTP download</h4>
          Genome-Scale Metabolic model files can be downloaded from <a href="https://ftp.icsb.chalmers.se">ftp.icsb.chalmers.se</a> or by connecting to the FTP using your favorite FTP client (e.g. <a href="https://filezilla-project.org/">FileZilla</a>).
          <br>
          <span class="has-text-weight-bold lab">Host:</span> <a href="https://ftp.icsb.chalmers.se">ftp.icsb.chalmers.se</a><br>
          <span class="has-text-weight-bold lab">Login:</span> (leave it empty)<br>
          <span class="has-text-weight-bold lab">Password:</span> (leave it empty)<br>
          <span class="has-text-weight-bold lab">Port:</span> 21
          <!-- ================ -->
          <h3 id="Resources">Resources</h3>
          List the most relevant software tools, algorithms or databases produced/published by the sysbio reaseerch group. Click on the left-side image/logo to navigate to the corresponding remote web resources.
          <!-- ================ -->
          <h3 id="Privacy">Privacy statement</h3>
          Metabolic Atlas gathers information about users solely to improve the usability and usefulness of the site. There are two types of cookie that are set by Metabolic Atlas:<br>
          <strong>Functionality cookies</strong> are used to personalize the appearence of the Metabolic Atlas.<br>
          <strong>Tracking cookies</strong> are used via private analytics to track the users on our website. We use them to anonymously observe the behaviour on our website in order to improve it. This information is not shared with any third party.

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
