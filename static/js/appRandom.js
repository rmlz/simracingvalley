angular.module('randomApp', ['angularUtils.directives.dirPagination'])

.controller('PageCtrl', function($scope, $http) {

  $scope.info = {}
  console.log('PAGECONTROL RUNNING')

  //$scope.roullete = function(cartrack){
  	//$scope.randomtrack = cartrack[0][Math.floor(Math.random()*cartrack[0].length)] 
 	//$scope.randomcar = cartrack[1][Math.floor(Math.random()*cartrack[1].length)]

  

  $scope.getrandom = function(){
     $http({
       method: 'POST',
       url: '/getRandom',
     }).then(function(response) {

       $scope.cartracklist = response.data;
        roullete = setInterval(function(){
        	rand = Math.random()
        	rand2 = Math.random()
        	console.log(rand, rand2)
       		$scope.randomtrack = $scope.cartracklist[0][Math.floor(rand*$scope.cartracklist[0].length)] 
 	    	$scope.randomcar = $scope.cartracklist[1][Math.floor(rand2*$scope.cartracklist[1].length)]
     

       },500);
        //setTimeout(function(){
        //	clearInterval(roulette);
       // }, (Math.random()*15 + 10)*10000)
       
      
       //console.log('mm', $scope.cartracklist)
       //console.log('ATORON', $scope.randomtrack, $scope.randomcar)
     },
     function(error) {
       console.log(error);
     });
   }
	
	

    
    
    
    
})
