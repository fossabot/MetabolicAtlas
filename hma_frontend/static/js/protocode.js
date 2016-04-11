// a very simple example of angular/cytoscape.js integration

// context (rightclick/2finger) drag to resize in graph
// use text boxes to resize in angular

var app = angular.module('app', []);

// use a factory instead of a directive, because cy.js is not just for visualisation;
// you need access to the graph model and events etc
app.factory('proteinGraph', [ '$q', function( $q ){
  var cy;
  var proteinGraph = function(proteins){
    var deferred = $q.defer();

    // put protein model list in in cy.js
    var eles = [];
    for( var i = 0; i < proteins.length; i++ ){
      eles.push({
        group: 'nodes',
        data: {
          id: proteins[i].id,
          weight: proteins[i].weight,
          name: proteins[i].name
        }
      });
    }

    for( var i = 1; i < proteins.length; i++ ){
      eles.push({
        group: 'edges',
        data: {
          id: proteins[0].id + '_' + proteins[i].id,
          source: proteins[0].id,
          target: proteins[i].id
        }
      });
    }

    $(function(){ // on dom ready

      cy = cytoscape({
        container: $('#cy')[0],

        style: cytoscape.stylesheet()
          .selector('node')
            .css({
              'content': 'data(name)',
              'height': 80,
              'width': 'mapData(weight, 1, 200, 1, 200)',
               'text-valign': 'center',
                'color': 'white',
                'text-outline-width': 2,
                'text-outline-color': '#888'
             })
          .selector('edge')
            .css({
              'width': 3,
              'line-color': '#ccc',
              'target-arrow-color': '#ccc',
              'target-arrow-shape': 'triangle'
            })
          .selector(':selected')
            .css({
              'background-color': 'black',
              'line-color': 'black',
              'target-arrow-color': 'black',
              'source-arrow-color': 'black',
              'text-outline-color': 'black'
          }),

        layout: {
          name: 'cose',
          padding: 10
        },

        elements: eles,

        ready: function(){
          deferred.resolve( this );

          cy.on('cxtdrag', 'node', function(e){
            var node = this;
            var dy = Math.abs( e.cyPosition.x - node.position().x );
            var weight = Math.round( dy*2 );

            node.data('weight', weight);

            fire('onWeightChange', [ node.id(), node.data('weight') ]);
          });
        }
      });

    }); // on dom ready

    return deferred.promise;
  };

  proteinGraph.listeners = {};

  function fire(e, args){
    var listeners = proteinGraph.listeners[e];

    for( var i = 0; listeners && i < listeners.length; i++ ){
      var fn = listeners[i];

      fn.apply( fn, args );
    }
  }

  function listen(e, fn){
    var listeners = proteinGraph.listeners[e] = proteinGraph.listeners[e] || [];

    listeners.push(fn);
  }

  proteinGraph.setProteinWeight = function(id, weight){
    cy.$('#' + id).data('weight', weight);
  };

  proteinGraph.onWeightChange = function(fn){
    listen('onWeightChange', fn);
  };

  return proteinGraph;


} ]);

app.controller('proteinsCtrl', [ '$scope', 'proteinGraph', function( $scope, proteinGraph ){
  var cy; // maybe you want a ref to cy
  // (usually better to have the srv as intermediary)

  $scope.proteins = [
    { id: 'p1', name: 'Protein1', weight: 65 },
    { id: 'p2', name: 'Protein2', weight: 110 },
    { id: 'p3', name: 'Protein3', weight: 30 },
    { id: 'p4', name: 'Protein4', weight: 150 }
  ];

  var proteinsById = {};
  for( var i = 0; i < $scope.proteins.length; i++ ){
    var p = $scope.proteins[i];

    proteinsById[ p.id ] = p;
  }

  // you would probably want some ui to prevent use of proteinsCtrl until cy is loaded
  proteinGraph( $scope.proteins ).then(function( proteinsCy ){
    cy = proteinsCy;

    // use this variable to hide ui until cy loaded if you want
    $scope.cyLoaded = true;
  });

  $scope.onWeightChange = function(Protein){
     proteinGraph.setProteinWeight( Protein.id, Protein.weight );
  };

  proteinGraph.onWeightChange(function(id, weight){
    proteinsById[id].weight = weight;

    $scope.$apply();
  });

} ]);

app.controller('PIDSearchController', ['$scope', function($scope) {
    $scope.PIDlist = [];
    $scope.PIDtext = 'hello';
    $scope.submit = function() {
      if ($scope.PIDtext) {
        $scope.PIDlist.push(this.PIDtext);
        $scope.PIDtext = '';
      }
    };
}]);
