# -*- coding: utf-8 -*-
"""module containg the API wrapper"""


import io
import requests
import yaml
from pysolar import solar
import pandas as pd


class EndpointWrapper:
    """Base class for endpoint wrapper
    The usage of the API requires an API key that can be requested for free at:
    "https://developer.nrel.gov/signup/"
    List of all Endpoints at:
    "https://developer.nrel.gov/docs/solar/nsrdb/"

    Parameters
    ----------
    latlong : tuple of list with latitude and longitude as decimal numbers
    config_path : absolute filepath, optional(default=None)
    request_attr_dict : dictonary, optinal(default=empty dict)
        Should contain parameters and values for the API call. Space character
        is not allowed and should be replaced with "+" in all string values
        Needs to contain Values for:
            api_key: string
            full_name: string
            email: string
            affiliation: string
            reason: string
            names: int or list of int, years that should be extracted
            mailing_list: string, possible values "true" and "false"
    """
    def __init__(self, endpoint_url, latlong, request_attr_dict=None,
                 config_path=None):
        self.endpoint_url = endpoint_url
        self.request_attr = {}
        self.df = pd.DataFrame()
        if config_path is not None:
            with open(config_path) as handle:
                config = yaml.load(handle)
            self.request_attr.update(config)
        if request_attr_dict is not None:
            self.request_attr.update(request_attr_dict)
        try:
            self.latitude, self.longitude = latlong
        except TypeError as e:
            raise TypeError('latlong needs to have exactly 2 values :{}'
                            .format(e))

    def request_data(self, parse_datetime=True):
        """Requests data from NSRDB server and converts it to a pandas
        dataframe
        Parameters
        ----------
        parse_datetime: Boolean, optional(default=True)
        If parse_datetime is set to True the original datetime defining columns
        are transformed to a pandas datetime column.
        """
        # NSRDB api does not support %formated url payloads
        payload_str = "&".join("%s=%s" % (k, v)
                               for k, v in self.request_attr.items())
        response = requests.get(self.endpoint_url, params=payload_str)
        if response.status_code != 200:
            raise Exception('''Request error with status code: {}\n
                            REsponse message:\n{}'''.format(
                                response.status_code, response.content))

        buffer = io.BytesIO(response.content)
        buffer.seek(0)
        self.df = pd.read_csv(buffer, skiprows=[0, 1])
        if parse_datetime:
            self.parse_datetime()

    def parse_datetime(self, drop_original=True):
        """Parsing the 5 datetime columns from the original NSRDB data to one
        pandas datetime column.
        Parameters
        ----------
        drop_original: Boolean, optional(default=True)
        If drop_original is set to True the original datetime defining columns
        are droped from the dataframe.
        """
        time_columns = ['Year', 'Month', 'Day', 'Hour', 'Minute']
        self.df[time_columns] = self.df[time_columns].astype(str)
        self.df['dt'] = pd.to_datetime(self.df.Year +
                                       self.df.Month.apply('{:0>2}'.format) +
                                       self.df.Day.apply('{:0>2}'.format) +
                                       self.df.Hour.apply('{:0>2}'.format) +
                                       self.df.Minute.apply('{:0>2}'.format),
                                       format='%Y%m%d%H%M')
        if drop_original:
            self.df = self.df.drop(time_columns, axis=1)

    def add_zenith_azimuth(self):
        """Adds zenith and azimuth from location and datetime with using
        pysolar. Datetime needs to be timezone aware.
        """
        self.df['zenith'] = \
            self.df.dt.apply(lambda x: solar.get_altitude(self.latitude,
                                                          self.longitude,
                                                          x))
        self.df['azimuth'] = \
            self.df.dt.apply(lambda x: solar.get_azimuth(self.latitude,
                                                         self.longitude,
                                                         x))


class SpectralTMYWrapper(EndpointWrapper):
    """Wrapper for Endpoint to download Spectral TMY Data
    The usage of the API requires an API key that can be requested for free at:
    "https://developer.nrel.gov/signup/"
    Documentation of the Endpoint at:
    "https://developer.nrel.gov/docs/solar/nsrdb/spectral_tmy_data_download/"

    Parameters
    ----------
    latlong : tuple of list with latitude and longitude as decimal numbers#
    config_path : absolute filepath, optional(default=None)
    request_attr_dict : dictonary, optinal(default=empty dict)
        Should contain parameters and values for the API call. Space character
        is not allowed and should be replaced with "+" in all string values
        Needs to contain Values for:
            api_key: string
            full_name: string
            email: string
            affiliation: string
            reason: string
            mailing_list: string, possible values "true" and "false"
    """
    def __init__(self, latlong, request_attr_dict=None, config_path=None):
        endpoint_url = \
            'http://developer.nrel.gov/api/solar/nsrdb_download.csv'

        EndpointWrapper.__init__(self, endpoint_url, latlong,
                                 request_attr_dict, config_path)

        valid_attributes = ['PW', 'AT', 'WS'] +\
            ['DNI_{}'.format(wl) for wl in range(300, 1810, 10)] +\
            ['GHI_{}'.format(wl) for wl in range(300, 1810, 10)]
        default_attr = {'names': 'tmy',
                        'utc': 'true',
                        'attributes': valid_attributes}
        self.request_attr = {**default_attr, **self.request_attr}
        assert(all([attrib in valid_attributes
                    for attrib in valid_attributes]))
