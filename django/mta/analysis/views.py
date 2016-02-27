from django.shortcuts import render
from django.template import loader
import pandas as pd
from django.http import HttpResponse
import json
from time import mktime
from datetime import datetime, date, timedelta
from .models import Stats


def index(request):

    return render(request, 'analysis/index.html', {
    })


date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime) or isinstance(obj, date)
    else None
)


def parseInputVariables(raw_get):
    ''' parses input vars '''
    input_data = {}
    ''' hack, but running low on time '''
    for i_key, key in enumerate(raw_get.iterkeys()):
        if i_key == 0:
            input_data = '[' + key + ']'
            continue

        print('other', i_key, key)

    input_data = json.loads(input_data)[0]
    input_data['date']['start'] = datetime.strptime(input_data['date']['start'], '%a %b %d %Y')
    input_data['date']['end'] = datetime.strptime(input_data['date']['end'], '%a %b %d %Y')
    input_data['date']['list'] = input_data['date']['list'].split('\n')
    input_data['date']['list'] = filter(None, input_data['date']['list'])
    for i_date, _date in enumerate(input_data['date']['list']):
        input_data['date']['list'][i_date] = datetime.strptime(_date, '%Y-%m-%d')

        # input_data['date']['list'][i_date] = date(
        #     input_data['date']['list'][i_date].year,
        #     input_data['date']['list'][i_date].month,
        #     input_data['date']['list'][i_date].day
        # )

        # print(input_data['date']['list'][i_date])
    input_data['time']['start_date'] = datetime.strptime(input_data['time']['start_date_corrected'], '%a %b %d %Y')
    input_data['time']['end_date'] = datetime.strptime(input_data['time']['end_date_corrected'], '%a %b %d %Y')

    input_data['date']['start'] = input_data['date']['start'].replace(
        hour=input_data['time']['start']['hours'],
        minute=input_data['time']['start']['minutes'],
        second=0,
    )
    # input_data['date']['start'] -= timedelta(seconds=1)

    input_data['date']['end'] = input_data['date']['end'].replace(
        hour=input_data['time']['end']['hours'],
        minute=input_data['time']['end']['minutes'],
        second=0,
    )

    input_data['date']['end'] += timedelta(minutes=1)

    return input_data


def get(request):

    # if request.method == 'GET':

    # print('REQUEST', request.GET.list())

    df_to_return = pd.DataFrame([])
    input_data = parseInputVariables(request.GET)

    print(input_data)

    raw_data = []
    if len(input_data['date']['list']) > 0:
        print('\n')
        print('LIST', input_data['date']['list'])
        raw_data = Stats.objects.filter(
            date__in=input_data['date']['list']
        )

    else:
        ''' add in time range '''
        print('\n')

        print('RANGE', input_data['date']['start'], input_data['date']['end'])
        raw_data = Stats.objects.filter(
            datetime__range=(
                input_data['date']['start'],
                input_data['date']['end'],
            )
        )

    df_time_series = pd.DataFrame()
    df_time_series = pd.DataFrame(list(raw_data.values()))

    if len(df_time_series) == 0:
        response_data = {
            'code': 'NO DATA',
            'when': datetime.now(),
            'results': [],
        }
        print('\n\n', 'No data')
        return HttpResponse(
            json.dumps(response_data,  default=date_handler),
            content_type="application/json"
        )
    df_time_series['date'] = df_time_series.datetime.apply(lambda t: t.date())

    if input_data['date']['bucket'] == 'Day':
        input_data['date']['bucket'] = 'date'
    if input_data['date']['bucket'] == 'Hour':
        df_time_series['hour'] = df_time_series.datetime.apply(lambda t: t.hour)
    elif input_data['date']['bucket'] == 'Minute':
        df_time_series['minute'] = df_time_series.datetime.apply(lambda t: t.hour * 60 + t.minute)

    ''' set split by '''
    if input_data['split_by'] == 'Station':
        pass
    elif input_data['split_by'] == 'SCP':
        pass
    elif input_data['split_by'] == 'Both':
        df_time_series['both'] = df_time_series.station + ' - ' + df_time_series.scp

    df_by_date = {}
    date_bucket_by = input_data['date']['bucket'].lower()
    stations_split_by = input_data['split_by'].lower()

    print('Bucket By:', date_bucket_by)
    print('Split By:', stations_split_by)

    for (i_grouping, ((_date_, station), data)) in enumerate(df_time_series.groupby([date_bucket_by, stations_split_by])):

        if station not in df_by_date:
            df_by_date[station] = {}

        if input_data['statistic'] == 'Entry':
            df_by_date[station][_date_] = data.entries.sum()
        elif input_data['statistic'] == 'Exit':
            df_by_date[station][_date_] = data.exits.sum()
        elif input_data['statistic'] == 'Busyness':
            df_by_date[station][_date_] = data.entries.sum() + data.exits.sum()

    df_to_return = pd.DataFrame(df_by_date)

    ''' fill in 0 '''
    df_to_return = df_to_return.fillna(0, axis=1)

    df_max = df_to_return.max()
    df_max.sort(ascending=False)

    df_min = df_to_return.min()
    df_min.sort(ascending=False)

    df_mean = df_to_return.mean()
    df_mean.sort(ascending=False)

    ''' ensure index known for js '''
    # df_to_return['_id'] = df_to_return.index

    response_data = {
        'code': 'GOOD',
        'when': datetime.now(),
        # 'results': df_to_return.to_dict(),
        'analysis': {
            'max': json.loads(df_max.to_json(orient='columns')),
            'min': json.loads(df_min.to_json(orient='columns')),
            'mean': json.loads(df_mean.to_json(orient='columns')),
            'raw': json.loads(df_to_return.to_json(orient='columns')),
        }
    }
    print('\n\n')
    return HttpResponse(
        json.dumps(response_data,  default=date_handler),
        content_type="application/json"
    )
    # else:
    #     return HttpResponse(
    #         json.dumps({
    #             'code': 'BAD',
    #             'when': datetime.now(),
    #         }),
    #         content_type="application/json"
    #     )
