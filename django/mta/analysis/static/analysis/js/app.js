agGrid.initialiseAgGridWithAngular1(angular);


angular.module('MTA', ['datePicker', "agGrid"])
    .config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    })
    .controller('input', ['$scope', '$http',
        function($scope, $http) {

            $scope.input = {
                statistic: 'Entry',
                type: 'Day',
                split_by: 'Station',
                date: {
                    start: moment(20130701, 'YYYYMMDD'),
                    end: moment(20130701, 'YYYYMMDD'),
                    list: '',
                    bucket: "Day",
                },
                time: {
                    start_date: new Date(2013, 7, 1, 0, 0, 0),
                    start: {
                        minutes: 59,
                        hours: 23
                    },
                    end_date: new Date(2013, 7, 1, 23, 59, 0),
                    end: {
                        minutes: 59,
                        hours: 23
                    }
                }
            }

            $scope.min_date = moment().year(2013).month(5).day(29);
            $scope.max_date = moment().year(2013).month(7).day(2);

            $scope.gridOptions = {
                columnDefs: [],
                rowData: [],
                rowSelection: 'multiple',
                enableColResize: true,
                enableSorting: true,
                enableFilter: true,
                groupHeaders: true,
                rowHeight: 22,
                suppressRowClickSelection: true

            };


            $scope.submit = function() {
                console.log('Getting data');
                // console.log($scope.input);

                $scope.input.time.start = {
                    minutes: $scope.input.time.start_date.getMinutes(),
                    hours: $scope.input.time.start_date.getHours(),
                }
                $scope.input.time.end = {
                    minutes: $scope.input.time.end_date.getMinutes(),
                    hours: $scope.input.time.end_date.getHours(),
                }

                $.ajax({
                    url: '/get',
                    data: JSON.stringify($scope.input),
                    success: function(data, status) {
                        // parse _id
                        console.log(data.results);

                        if (data.results.length == 0) return;

                        var cols = [];
                        for (var key in data.results[0]) {


                            if (key == '_id') {
                                cols.unshift({
                                    headerName: 'Bucket',
                                    field: key
                                })

                                /**
                                 * Change to datetime
                                 */
                                if($scope.input.date.bucket == "Day"){
                                  data.results.forEach(function(row) {
                                      row._id = new Date(row._id)
                                  })
                                } else if($scope.input.date.bucket == "Hour"){
                                  data.results.forEach(function(row) {

                                    when = "am";
                                    if(row._id > 12){
                                      row._id -= 12;
                                      when = "pm";
                                    }

                                    row._id = row._id.toString() + ' ' + when;
                                  })
                                }
                                continue;
                            }

                            cols.push({
                                headerName: key,
                                field: key
                            })
                        }





                        $scope.gridOptions.api.setRowData(data.results);
                        $scope.gridOptions.api.setColumnDefs(cols);

                        $scope.$apply();
                        $scope.gridOptions.api.refreshView();
                    }
                })

                // $http.get('/get', data).success(function(data, status){

                // // $http.get('get?' + JSON.stringify({a: 123}) ).success(function(data, status){
                //   console.log(data, status);
                // })
                // $http({
                //   method: 'GET',
                //   url: '/get',
                //   data: $scope.input
                // }).then(function successCallback(response) {

                //   console.log(response.data);
                //   }, function errorCallback(response) {

                //     console.log('error', response);
                //   });

            }



        }
    ]);
