var app = angular.module('myApp', ['angularUtils.directives.dirPagination'])

app.controller('globalRankCtrl', function($scope, $http) {


  $scope.info = {}
  $scope.currentPage = 1

  $scope.showlist = function(){
     $http({
       method: 'POST',
       url: '/getDriverList',
     }).then(function(response) {
       $scope.drivers = response.data;
       console.log('mm', $scope.drivers)
     },
     function(error) {
       console.log(error);
     });
   }



//-----------------------------------------------------------
   $scope.reverse = true
   $scope.showlist()
   $scope.sortKey = 'Points'

   $scope.sort = function(keyname){
     console.log(keyname) //sort the table values
     $scope.sortKey = keyname //set the sortBy to param passed
     $scope.reverse = !$scope.reverse //if true goes false, vice versa
     console.log('jj', $scope.reverse)
   };


				$scope.addDriver = function(){
					$http({
						method: 'POST',
						url: '/addDriver',
						data: {info:$scope.info}
					}).then(function(response) {
						$scope.showlist();
						$('#addPopUp').modal('hide')
						$scope.info = {}
					}, function(error) {
						console.log(error);
					});
				}

				$scope.showDriver = function(id){
					$scope.info.id = id;

					$scope.showAdd = false;

					$http({
						method: 'POST',
						url: '/getDriver',
						data: {id:$scope.info.id}
					}).then(function(response) {
						console.log(response);
						$scope.info = response.data;
						$('#driverPopUp').modal('show')
					}, function(error) {
						console.log(error);
					});
				}

				$scope.updateDriver = function(id){

					$http({
						method: 'POST',
						url: '/updateDriver',
						data: {info:$scope.info}
					}).then(function(response) {
						console.log(response.data);
						$scope.showlist();
						$('#addPopUp').modal('hide')
					}, function(error) {
						console.log(error);
					});
				}


				$scope.showAddPopUp = function(){
					$scope.showAdd = true;
					$scope.info = {};
					$('#addPopUp').modal('show')
				}

				$scope.showRunPopUp = function(id){

					$scope.info.id = id;
					$scope.run = {};
					$http({
						method: 'POST',
						url: '/getDriver',
						data: {id:$scope.info.id}
					}).then(function(response) {
						console.log(response);
						$scope.run = response.data;
						$scope.run.isRoot = false;
						$('#runPopUp').modal('show');
					}, function(error) {
						console.log(error);
					});



				}

				$scope.confirmDelete = function(id){
					$scope.deleteDriverId = id;
					$('#deleteConfirm').modal('show');
				}

				$scope.deleteDriver = function(){

					$http({
						method: 'POST',
						url: '/deleteDriver',
						data: {id:$scope.deleteDriverId}
					}).then(function(response) {
						console.log(response.data);
						$scope.deleteDriverId = '';
						$scope.showlist();
						$('#deleteConfirm').modal('hide')
					}, function(error) {
						console.log(error);
					});
				}


				$scope.executeCommand = function(){
          console.log($scope.run)
          $http({
            method: 'POST',
						url: '/execute',
						data: {info:$scope.run}
					}).then(function(response) {
            console.log(response);
            $scope.run.response = response.data.message;
					}, function(error) {
						console.log(error);
					});
				}


      }

    );

app.controller('ftRankCtrl', function($scope, $http) {


  $scope.info = {}
  $scope.currentPage = 1

  $scope.showlist = function(){
     $http({
       method: 'POST',
       url: '/getDriverList2',
     }).then(function(response) {
       $scope.drivers = response.data;
       console.log('mm', $scope.drivers)
     },
     function(error) {
       console.log(error);
     });
   }



//-----------------------------------------------------------
   $scope.reverse = true
   $scope.showlist()
   $scope.sortKey = 'Points'

   $scope.sort = function(keyname){
     console.log(keyname) //sort the table values
     $scope.sortKey = keyname //set the sortBy to param passed
     $scope.reverse = !$scope.reverse //if true goes false, vice versa
     console.log('jj', $scope.reverse)
   };


				$scope.addDriver = function(){
					$http({
						method: 'POST',
						url: '/addDriver',
						data: {info:$scope.info}
					}).then(function(response) {
						$scope.showlist();
						$('#addPopUp').modal('hide')
						$scope.info = {}
					}, function(error) {
						console.log(error);
					});
				}

				$scope.showDriver = function(id){
					$scope.info.id = id;

					$scope.showAdd = false;

					$http({
						method: 'POST',
						url: '/getDriver',
						data: {id:$scope.info.id}
					}).then(function(response) {
						console.log(response);
						$scope.info = response.data;
						$('#driverPopUp').modal('show')
					}, function(error) {
						console.log(error);
					});
				}

				$scope.updateDriver = function(id){

					$http({
						method: 'POST',
						url: '/updateDriver',
						data: {info:$scope.info}
					}).then(function(response) {
						console.log(response.data);
						$scope.showlist();
						$('#addPopUp').modal('hide')
					}, function(error) {
						console.log(error);
					});
				}


				$scope.showAddPopUp = function(){
					$scope.showAdd = true;
					$scope.info = {};
					$('#addPopUp').modal('show')
				}

				$scope.showRunPopUp = function(id){

					$scope.info.id = id;
					$scope.run = {};
					$http({
						method: 'POST',
						url: '/getDriver',
						data: {id:$scope.info.id}
					}).then(function(response) {
						console.log(response);
						$scope.run = response.data;
						$scope.run.isRoot = false;
						$('#runPopUp').modal('show');
					}, function(error) {
						console.log(error);
					});



				}

				$scope.confirmDelete = function(id){
					$scope.deleteDriverId = id;
					$('#deleteConfirm').modal('show');
				}

				$scope.deleteDriver = function(){

					$http({
						method: 'POST',
						url: '/deleteDriver',
						data: {id:$scope.deleteDriverId}
					}).then(function(response) {
						console.log(response.data);
						$scope.deleteDriverId = '';
						$scope.showlist();
						$('#deleteConfirm').modal('hide')
					}, function(error) {
						console.log(error);
					});
				}


				$scope.executeCommand = function(){
          console.log($scope.run)
          $http({
            method: 'POST',
						url: '/execute',
						data: {info:$scope.run}
					}).then(function(response) {
            console.log(response);
            $scope.run.response = response.data.message;
					}, function(error) {
						console.log(error);
					});
				}


      }

    );
