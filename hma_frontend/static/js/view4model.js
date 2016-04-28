
var app = angular.module('app', []);

app.factory('view4Graph', [ '$q', function( $q ){
  var cy;
  var view4Graph = function(elms, rels){
    var deferred = $q.defer();

    var elmsjson = [];
    for( var i = 0; i < elms.length; i++ ){
      if (elms[i].parentid!='null') {
        elmsjson.push({
          group: 'nodes',
          data: {
            id: elms[i].id,
            parent: elms[i].parentid,
            name: elms[i].short,
          }
        });
      } else {
        elmsjson.push({
          group: 'nodes',
          data: {
            id: elms[i].id,
            name: elms[i].short,
          }
        });
      }

    }

    for( var i = 0; i < rels.length; i++ ){
      elmsjson.push({
        group: 'edges',
        data: {
          id: rels[i].id,
          source: rels[i].source,
          target: rels[i].target
        }
      });
    }

    console.log('cy json:'+JSON.stringify(elmsjson));

    $(function(){ // on dom ready

      cy = cytoscape({
        container: $('#cy')[0],

        style: cytoscape.stylesheet()
        .selector('node')
        .css({
            'content': 'data(name)',
            'font-size': "42px",
            //'height': 80,
            //'width': 'mapData(weight, 1, 200, 1, 200)',
            'text-valign': 'center',
            'text-halign': 'center'
            //'color': 'white',
            //'text-outline-width': 2,
            //'text-outline-color': '#888'
        })
        .selector('$node > node')
        .css({
            'font-size': "82px",
            'padding-top': '1px',
            'padding-left': '1px',
            'padding-bottom': '1px',
            'padding-right': '1px',
            'text-valign': 'top',
            'text-halign': 'center',
            'background-color': '#bbb'
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
          name: 'random'
        },

        elements: elmsjson,

        ready: function(){
          deferred.resolve( this );

          cy.on('cxtdrag', 'node', function(e){
            /*
            var node = this;
            var dy = Math.abs( e.cyPosition.x - node.position().x );
            var weight = Math.round( dy*2 );

            node.data('weight', weight);

            fire('onWeightChange', [ node.id(), node.data('weight') ]);
            */
          });
        }
      });

    }); // on dom ready

    return deferred.promise;
  };

  view4Graph.listeners = {};

  function fire(e, args){
    var listeners = view4Graph.listeners[e];

    for( var i = 0; listeners && i < listeners.length; i++ ){
      var fn = listeners[i];

      fn.apply( fn, args );
    }
  }

  function listen(e, fn){
    var listeners = view4Graph.listeners[e] = view4Graph.listeners[e] || [];

    listeners.push(fn);
  }

  view4Graph.onSelected = function(fn){
    listen('onSelected', fn);
  };

  return view4Graph;


} ]);
