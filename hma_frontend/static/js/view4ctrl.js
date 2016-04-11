app.controller('v4ElemsCtrl', [ '$scope', 'view4Graph', function( $scope, view4Graph ){
  var cy; // mitght want a ref to cy
  // (usually better to have the srv as intermediary)

  $scope.elms = [
    { id: 'e1', parentid: 'null', type:'E', short:'E1', long:'long E1', description:'super long E1', formula: 'E1f' },
    { id: 'r1', parentid: 'null', type:'R', short:'R1', long:'long R1', description:'super long R1', formula: 'R1f' },
    { id: 'r2', parentid: 'null', type:'R', short:'R2', long:'long R2', description:'super long R2', formula: 'R2f' },
    { id: 'm1', parentid: 'r1', type:'M', short:'M1', long:'long M1', description:'super long M1', formula: 'M1f' },
    { id: 'm2', parentid: 'r1', type:'M', short:'M2', long:'long M2', description:'super long M2', formula: 'M2f' },
    { id: 'm3', parentid: 'r2', type:'M', short:'M3', long:'long M3', description:'super long M3', formula: 'M3f' },
    { id: 'm4', parentid: 'r2', type:'M', short:'M1', long:'long M1', description:'super long M1', formula: 'M1f' }
  ];

  $scope.rels = [
    { id: 'e1_r1', source: 'e1', target: 'r1' },
    { id: 'e1_r2', source: 'e1', target: 'r2' }
  ];

  var elmsById = {};
  for( var i = 0; i < $scope.elms.length; i++ ){
    var p = $scope.elms[i];

    elmsById[ p.id ] = p;
  }

  // might want some ui to prevent use of this controller until cy is loaded
  view4Graph( $scope.elms, $scope.rels ).then(function( elmsCy ){
    cy = elmsCy;

    // hide ui until cy loaded
    $scope.cyLoaded = true;
  });

  $scope.onSelected = function(elem){
     //Nothing happens rite now
  };

} ]);
