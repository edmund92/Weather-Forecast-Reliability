import urllib.parse
import requests
from datetime import datetime
from datetime import date
from datetime import time
import copy
import calendar
import pprint


def get_latitude(arr_index):
    return weatherData['metadata']['stations'][arr_index]['location']['latitude']


def get_longitude(arr_index):
    return weatherData['metadata']['stations'][arr_index]['location']['longitude']


def get_rainfall_value(arr_index):
    return weatherData['items'][0]['readings'][arr_index]['value']


def get_station_id(arr_index):
    return weatherData['metadata']['stations'][arr_index]['id']


def get_timestamp(s):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S+08:00').time()


def sort_value(dict, day):
    for n in dict['readings']:
        if n['station_id'] in day['North']:
            day['North'][(n['station_id'])] += n['value']
        elif n['station_id'] in day['South']:
            day['South'][(n['station_id'])] += n['value']
        elif n['station_id'] in day['East']:
            day['East'][(n['station_id'])] += n['value']
        elif n['station_id'] in day['West']:
            day['West'][(n['station_id'])] += n['value']
        elif n['station_id'] in day['Central']:
            day['Central'][(n['station_id'])] += n['value']


def assign_value_for_forecast(dict, day):
    global reliabilityDenominator
    global reliabilityNumerator
    for area, forecast in dict['regions'].items():
        if ('Cloud' in forecast) or ('Fair' in forecast):
            for i in day[area.capitalize()].values():
                if i > 1:
                    reliabilityDenominator += 1
                    break
                else:
                    reliabilityNumerator += 1
                    reliabilityDenominator += 1
        else:
            for i in day[area.capitalize()].values():
                if i < 1:
                    reliabilityDenominator += 1
                    break
                else:
                    reliabilityNumerator += 1
                    reliabilityDenominator += 1


year = int(input('Year: '))
month = int(input('Month in number: '))

for day in range(1, calendar.monthrange(year, month)[1] + 1):

    print(year)
    print(day)
    dailyData = {'North': {}, 'South': {}, 'East': {}, 'West': {}, 'Central': {}}
    dates = str(date(year, month, day))
    weatherUrl = 'https://api.data.gov.sg/v1/environment/rainfall?date=' + dates
    weatherData = requests.get(weatherUrl).json()

    for i in range(len(weatherData['metadata']['stations'])):

        if (1.35891 <= get_latitude(i)) and (103.73982 <= get_longitude(i) <= 103.86121):
            dailyData['North'][get_station_id(i)] = 0
        elif (get_latitude(i) <= 1.3065) and (103.73982 <= get_longitude(i) <= 103.9105):
            dailyData['South'][get_station_id(i)] = 0
        elif (1.273956 <= get_latitude(i) <= 1.358913) and (103.73982 <= get_longitude(i) <= 103.86121):
            dailyData['Central'][get_station_id(i)] = 0
        elif get_longitude(i) <= 103.73982:
            dailyData['West'][get_station_id(i)] = 0
        elif get_longitude(i) >= 103.86121:
            dailyData['East'][get_station_id(i)] = 0

    morningData = copy.deepcopy(dailyData)
    afternoonData = copy.deepcopy(dailyData)
    eveningData = copy.deepcopy(dailyData)
    dailyData.clear()

    for i in weatherData['items']:
        # if get_timestamp(i['timestamp']) < time(6, 0):
        #     sort_value(i, morningData)
        if time(6, 0, 0) <= get_timestamp(i['timestamp']) < time(12, 0, 0):
            sort_value(i, morningData)
        elif time(12, 0, 0) <= get_timestamp(i['timestamp']) < time(18, 0, 0):
            sort_value(i, afternoonData)
        elif get_timestamp(i['timestamp']) >= time(18, 0, 0):
            sort_value(i, eveningData)

    # pprint.pprint(morningData)
    # print()
    # pprint.pprint(afternoonData)
    # print()
    # pprint.pprint(eveningData)
    # print()

    reliabilityNumerator = 0
    reliabilityDenominator = 0
    forecastUrl = 'https://api.data.gov.sg/v1/environment/24-hour-weather-forecast?date_time=' + dates + 'T00%3A00%3A00'
    forecastData = requests.get(forecastUrl).json()

    for i in forecastData['items'][0]['periods']:
        # if get_timestamp(['time']['start']) == time(0):
        #     assign_value_for_forecast(i, preDawnForecast)
        if get_timestamp(i['time']['start']) == time(6):
            assign_value_for_forecast(i, morningData)
        elif get_timestamp(i['time']['start']) == time(12):
            assign_value_for_forecast(i, afternoonData)
        elif get_timestamp(i['time']['start']) == time(18):
            assign_value_for_forecast(i, eveningData)

reliability = str(round((reliabilityNumerator/reliabilityDenominator)*100, 2))
print('Forecast reliability for', calendar.month_name[month], str(year) + ' is:', reliability + '%')
