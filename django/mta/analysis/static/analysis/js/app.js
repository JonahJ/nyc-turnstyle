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

            $scope.gridOptionsMax = {
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

            $scope.gridOptionsMin = {
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

            $scope.gridOptionsMean = {
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

                if ($scope.input.type == 'Day') {
                    $scope.input.date.end = $scope.input.date.start;
                }

                $scope.input.time.start = {
                    minutes: $scope.input.time.start_date.getMinutes(),
                    hours: $scope.input.time.start_date.getHours(),
                }
                $scope.input.time.end = {
                    minutes: $scope.input.time.end_date.getMinutes(),
                    hours: $scope.input.time.end_date.getHours(),
                }

                $scope.gridOptions.api.setRowData([]);
                $scope.gridOptions.api.setColumnDefs([]);
                $scope.gridOptionsMax.api.setRowData([]);
                $scope.gridOptionsMax.api.setColumnDefs([]);
                $scope.gridOptionsMin.api.setRowData([]);
                $scope.gridOptionsMin.api.setColumnDefs([]);
                $scope.gridOptionsMean.api.setRowData([]);
                $scope.gridOptionsMean.api.setColumnDefs([]);

                $scope.gridOptions.api.refreshView();
                $scope.gridOptionsMax.api.refreshView();
                $scope.gridOptionsMin.api.refreshView();
                $scope.gridOptionsMean.api.refreshView();


                var to_send = _.clone($scope.input);


                // console.log(to_send.time.start_date, to_send.time.start_date.toString().substring(0, 15));
                to_send.date.start = to_send.date.start.toString().substring(0, 15);
                to_send.date.end = to_send.date.end.toString().substring(0, 15);
                to_send.time.start_date_corrected = to_send.time.start_date.toString().substring(0,  15);
                to_send.time.end_date_corrected = to_send.time.end_date.toString().substring(0,  15);

                console.log(to_send);
                $.ajax({
                    url: '/get',
                    data: JSON.stringify(to_send),
                    success: function(data, status) {
                        // parse _id
                        console.log(data);

                        var getTableData = function(data) {
                            var raw_rows = [];
                            var raw_cols = [];

                            /**
                             * Add Rows for full table
                             */

                            for (var split_on in data) {
                                if (raw_cols.length == 0) {

                                    if (typeof data[split_on] === "object") {
                                        raw_cols.push({
                                            headerName: 'Split on',
                                            field: 'name',
                                        })
                                        for (var key in data[split_on]) {
                                            if ($scope.input.date.bucket == "Day") {

                                                raw_cols.push({
                                                    headerName: (new Date(parseInt(key))).toString(),
                                                    field: key
                                                })
                                            } else if ($scope.input.date.bucket == "Hour") {
                                                when = "am";
                                                time = key
                                                if (time > 12) {
                                                    time -= 12;
                                                    when = "pm";
                                                }

                                                time = time.toString() + ' ' + when;

                                                raw_cols.push({
                                                    headerName: time,
                                                    field: key
                                                })
                                            } else if ($scope.input.date.bucket == "Minute") {
                                                raw_cols.push({
                                                    headerName: key,
                                                    field: key
                                                })
                                            }
                                        }
                                    } else {
                                      raw_cols.push({
                                        headerName: 'Split on',
                                        field: 'name',
                                      });
                                      raw_cols.push({
                                        headerName: $scope.input.statistic,
                                        field: 'value',
                                      });
                                    }
                                }


                                if (typeof data[split_on] === "object") {
                                  data[split_on].name = split_on;
                                  raw_rows.push(data[split_on]);
                                } else {

                                  console.log(typeof data[split_on]);
                                  var row = {
                                    name: split_on,
                                    value: data[split_on]
                                  }
                                  raw_rows.push(row);
                                }
                            }

                            return {
                                rows: raw_rows,
                                cols: raw_cols
                            }
                        }


                        var raw = getTableData(data.results)
                        var max = getTableData(data.analysis.max);
                        var min = getTableData(data.analysis.min);
                        var mean = getTableData(data.analysis.mean);

                        /**
                         * For  'results': json.loads(df_to_return.to_json(orient='records')),
                         */
                        // if (data.results.length == 0) return;
                        // var raw_cols = [];
                        // for (var key in data.results[0]) {


                        //     if (key == '_id') {
                        //         raw_cols.unshift({
                        //             headerName: 'Bucket',
                        //             field: key
                        //         })

                        //         /**
                        //          * Change to datetime
                        //          */
                        //         if($scope.input.date.bucket == "Day"){
                        //           data.results.forEach(function(row) {
                        //               row._id = new Date(row._id)
                        //           })
                        //         } else if($scope.input.date.bucket == "Hour"){
                        //           data.results.forEach(function(row) {

                        //             when = "am";
                        //             if(row._id > 12){
                        //               row._id -= 12;
                        //               when = "pm";
                        //             }

                        //             row._id = row._id.toString() + ' ' + when;
                        //           })
                        //         }
                        //         continue;
                        //     }

                        //     raw_cols.push({
                        //         headerName: key,
                        //         field: key
                        //     })
                        // }

                        $scope.gridOptions.api.setRowData(raw.rows);
                        $scope.gridOptions.api.setColumnDefs(raw.cols);
                        $scope.gridOptionsMax.api.setRowData(max.rows);
                        $scope.gridOptionsMax.api.setColumnDefs(max.cols);
                        $scope.gridOptionsMin.api.setRowData(min.rows);
                        $scope.gridOptionsMin.api.setColumnDefs(min.cols);
                        $scope.gridOptionsMean.api.setRowData(mean.rows);
                        $scope.gridOptionsMean.api.setColumnDefs(mean.cols);



                        $scope.$apply();
                        $scope.gridOptions.api.refreshView();
                        $scope.gridOptionsMax.api.refreshView();
                        $scope.gridOptionsMin.api.refreshView();
                        $scope.gridOptionsMean.api.refreshView();
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
