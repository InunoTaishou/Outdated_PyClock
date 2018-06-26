import requests
import datetime


class Location:
    def __init__(self, city=None, state=None, zipcode=None):
        self.__city = None
        self.__state = None
        self.__state_abrv = None
        self.__zipcode = 0
        self.__country = None
        self.__country_abrv = None
        self.__lat = 0
        self.__lng = 0
        self.__request = None
        self.__request_on = None
        self.__request_type = None
        self.get_location(city, state, zipcode)

    def get_location(self, city=None, state=None, zipcode=None):
        self.__request_on = datetime.datetime.now()
        if zipcode:
            self.__request_type = 'zipcode'
            self.zipcode_to_location(zipcode)
        elif city and state:
            self.__request_type = 'city'
            self.city_to_location(city, state)
        else:
            try:
                current = requests.get('http://ipinfo.io/json').json()
                postal = current['postal']
                self.get_location(zipcode=postal)
            except OSError:
                pass

    def zipcode_to_location(self, zipcode):
        if zipcode:
            self.__request = self.__make_request(
                'https://maps.googleapis.com/maps/api/geocode/json?address=' + str(zipcode))

            if self.__request and len(self.__request) == 2:
                self.__city = self.__request['results'][0]['address_components'][1]['long_name']
                self.__state = self.__request['results'][0]['address_components'][3]['long_name']
                self.__state_abrv = self.__request['results'][0]['address_components'][3]['short_name']
                self.__country = self.__request['results'][0]['address_components'][4]['long_name']
                self.__country_abrv = self.__request['results'][0]['address_components'][4]['short_name']
                self.__zipcode = self.__request['results'][0]['address_components'][0]['long_name']
                self.__lat = self.__request['results'][0]['geometry']['location']['lat']
                self.__lng = self.__request['results'][0]['geometry']['location']['lng']
                return True

    def city_to_location(self, city, state):
        if city and state:
            self.__request = self.__make_request(
                'https://maps.googleapis.com/maps/api/geocode/json?address=' + city.replace(' ', '_') + ',' + state)
            if self.__request:
                self.__city = self.__request['results'][0]['address_components'][0]['long_name']
                self.__state = self.__request['results'][0]['address_components'][2]['long_name']
                self.__state_abrv = self.__request['results'][0]['address_components'][2]['short_name']
                self.__country = self.__self.__request['results'][0]['address_components'][3]['long_name']
                self.__country_abrv = request['results'][0]['address_components'][3]['short_name']
                self.__lat = self.__request['results'][0]['geometry']['location']['lat']
                self.__lng = self.__request['results'][0]['geometry']['location']['lng']
                return True

    @staticmethod
    def __make_request(url):
        try:
            return requests.get(url).json()
        except requests.exceptions.ConnectionError:
            return None

    @property
    def city(self):
        return self.__city

    @property
    def state(self):
        return self.__state

    @property
    def state_abrv(self):
        return self.__state_abrv

    @property
    def zipcode(self):
        return self.__zipcode

    @property
    def country(self):
        return self.__country

    @property
    def country_abrv(self):
        return self.__country_abrv

    @property
    def latitude(self):
        return self.__lat

    @property
    def longitude(self):
        return self.__lng

    @property
    def lat_lng(self):
        return [self.__lat, self.__lng]

    @state.setter
    def state(self, state):
        if self.__state != state:
            self.__state = state

    @city.setter
    def city(self, city):
        if self.__city != city:
            self.__city = city

    @zipcode.setter
    def zipcode(self, zipcode):
        if isinstance(zipcode, int) or isinstance(zipcode, float):
            zipcode = str(int(zipcode))
        if self.__zipcode != zipcode:
            self.__zipcode = zipcode
