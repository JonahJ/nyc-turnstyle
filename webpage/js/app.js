angular.module('MTA', ['datePicker'])
    .config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    })
    .controller('input', ['$scope', function($scope) {

      $scope.input = {
        statistic: 'Entry',
        datetype: 'Day',
        date: {
          start: moment().year(2013),
          end: moment().year(2013),
          list: '',
          bucket: "Day",
        },
        time: {
          start: new Date(0,0,0,0,0,0),
          end: new Date(0,0, 0,23,59,0),
        }
      }

      $scope.min_date = moment().year(2013).month(6).day(1);

      $scope.max_date = moment().year(2013).month(8).day(2);

      $scope.submit = function(){
        console.log('Getting data');
        console.log($scope.input);

      }
    }]);
