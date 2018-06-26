# -*- coding: utf-8 -*-
from forecastiopy import *
from location import *
import datetime
import time


class Weather:
    def __init__(self, api_key=None, location=None):
        if not location:
            location = Location()
        if not api_key:
            api_key = '847ee36436425fae33a2b4c82c534b76'

        self.__updated = None
        self.__location = location
        self.__forecast = None
        self.__currently = None
        self.__daily = None
        self.__api_key = api_key
        self.__date_format = '%I:%M %p %b %d, %Y'
        self._fahrenheit = 'fahrenheit'
        self._temp_unit_proper = 'Fahrenheit'
        self._temp_unit_abrv = '°F'
        self.__weather_keys = ['summary',
                               'temperature',
                               'apparentTemperature',
                               'temperatureMax',
                               'temperatureMin',
                               'humidity',
                               'windSpeed']
        self.__weather_prefix = ['',
                                 'Temperature: ',
                                 'Feels Like: ',
                                 'Day: ',
                                 'Night: ',
                                 'Humidity: ',
                                 'Wind: ']
        self.__cardinal_direction = ['N', 'N-NE', 'NE', 'E-NE', 'E', 'E-SE', 'SE',
                                     'S-SE', 'S', 'S-SW', 'SW', 'W-SW', 'W', 'W-NW', 'NW', 'N-NW']

    def get_forecast(self):
        if not (self.__location.latitude or self.__location.longitude):
            if not self.__location.get_location():
                return False
        try:
            self.__forecast = ForecastIO.ForecastIO(self.__api_key,
                                                    latitude=self.__location.latitude,
                                                    longitude=self.__location.longitude,
                                                    exclude=('minutely', 'hourly', 'flags'))

            if self.__forecast.has_daily() is True:
                self.__daily = FIODaily.FIODaily(self.__forecast)
            else:
                return False
            if self.__forecast.has_currently() is True:
                self.__currently = FIOCurrently.FIOCurrently(self.__forecast)
            self.__updated = datetime.datetime.now().timetuple()
        except OSError:
            return False
        return True

    def seconds_since_update(self):
        return int(time.mktime(datetime.datetime.now().timetuple()) - time.mktime(self.__updated))

    def minutes_since_update(self):
        return self.seconds_since_update() / 60

    def hours_since_update(self):
        return self.minutes_since_update() / 60

    def weather_string(self, summary=None, day=0):
        if not summary or not isinstance(summary, self.Summary):
            summary = self.get_summary(day)
        if not summary or not isinstance(summary, self.Summary):
            return 'Failed to retrieve forecast for ' + str(day)

        string = ''
        if summary.summary:
            string += summary.summary + '\n'
        if summary.current_temperature is not None:
            string += 'Currently: ' + self.__proper_temperature(summary.current_temperature, self._fahrenheit, self._temp_unit_abrv) + '\n'
        if summary.apparent_temperature is not None:
            string += 'Feels Like: ' + self.__proper_temperature(summary.apparent_temperature, self._fahrenheit, self._temp_unit_abrv) + '\n'
        if summary.temperature_max is not None:
            string += 'High: ' + self.__proper_temperature(summary.temperature_max, self._fahrenheit, self._temp_unit_abrv) + '\n'
        if summary.temperature_min is not None:
            string += 'Low: ' + self.__proper_temperature(summary.temperature_min, self._fahrenheit, self._temp_unit_abrv) + '\n'
        if summary.humidity is not None:
            string += 'Humidity: ' + str(summary.humidity) + '%\n'
        if summary.wind_bearing is not None and summary.wind_speed is not None:
            string += 'Wind: ' + str(summary.wind_speed) + ' MPH ' + self.__cardinal_direction[(summary.wind_bearing % 16)]
        return string

    @staticmethod
    def __proper_temperature(temperature, fahrenheit, unit):
        return str(temperature) + ' °F' \
                if fahrenheit else \
                str(round(((temperature - 32) * 5) / 9, 2)) + unit

    class Summary:
        def __init__(self, daily, day_number):
            self.day_number = day_number
            self.current_temperature = None
            self.apparent_temperature = None

            if 'time' in daily:
                self.day = datetime.datetime.fromtimestamp(daily['time']).strftime('%A')
            else:
                self.day = '...'

            if 'summary' in daily:
                self.summary = daily['summary']
            else:
                self.summary = 'Unknown'

            if 'icon' in daily:
                self.icon = daily['icon']
            else:
                self.icon = ''

            if 'temperatureMin' in daily:
                self.temperature_min = daily['temperatureMin']
            else:
                self.temperature_min = '0'

            if 'temperatureMax' in daily:
                self.temperature_max = daily['temperatureMax']
            else:
                self.temperature_max = '9999'

            if 'windSpeed' in daily:
                self.wind_speed = daily['windSpeed']
            else:
                self.wind_speed = '0'

            if 'humidity' in daily:
                self.humidity = str(int(float(daily['humidity']) * 100))
            else:
                self.humidity = '0'

            if 'windBearing' in daily:
                self.wind_bearing = daily['windBearing']
            else:
                self.wind_bearing = 'NA'

    def get_summary(self, day):
        if isinstance(day, str):
            day = day.lower()
            if day == 'today':
                day = 0
            elif day == 'tomorrow':
                day = 1
            elif day.isnumeric():
                day = int(day)
            else:
                try:
                    day = int(datetime.datetime.strftime(datetime.datetime.strptime(day, "%m/%d/%Y"), "%d")) - int(
                        datetime.datetime.strftime(datetime.datetime.now(), "%d"))
                except ValueError:
                    return None
        try:
            day = int(day)
        except ValueError:
            pass
            #return False

        #if day is None or day < 0:
        #   return False

        #if self.__forecast is None:
        #    if not self.get_forecast():
        #        return False

        #if day >= self.__daily.days():
        #    return False
        #    return False

        self.get_forecast()

        summary = self.Summary(self.__daily.get_day(day), day)

        if day == 0:
            summary.current_temperature = self.__currently.temperature
            summary.apparent_temperature = self.__currently.apparentTemperature
            summary.day = 'Today'

        return summary
