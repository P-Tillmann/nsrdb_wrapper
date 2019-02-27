# -*- coding: utf-8 -*-
"""Test Module"""

import os
import pandas as pd
import numpy as np
from nsrdb_wrapper import EndpointWrapper, SpectralTMYWrapper


def test_base_wrapper_init():
    """Test for initilizing generic wrapper"""
    config_path = os.path.abspath('tests/test_config.yaml')
    wrapper = EndpointWrapper('test_url', (40, 60), {'a': 'b'}, config_path)
    assert wrapper.latitude == 40
    assert wrapper.longitude == 60
    assert wrapper.endpoint_url == 'test_url'
    assert(wrapper.request_attr == {
        'api_key': 'Your-API-Key,',
        'leap_year': 'false,',
        'interval': '30,',
        'utc': 'true,',
        'full_name': 'FirstName+LastName,',
        'reason': 'Your+Reason,',
        'affiliation': 'Your+Affiliation,',
        'email': 'YourEmailAdress,',
        'mailing_list': True,
        'a': 'b'})


def test_spectmy_wrapper_init():
    """Test for initiliazing spectral tmy wrapper"""
    config_path = os.path.abspath('tests/test_config.yaml')
    wrapper = SpectralTMYWrapper((40, 60), {'a': 'b'}, config_path)
    assert wrapper.latitude == 40
    assert wrapper.longitude == 60
    assert(wrapper.endpoint_url ==
           'http://developer.nrel.gov/api/solar/nsrdb_download.csv')


def test_parse_time():
    """Test for parsing original datetime information to pandas datetime"""
    wrapper = EndpointWrapper('test_url', (40, 60), {'a': 'b'})
    wrapper.df = pd.DataFrame({'Year': [1990, 2001],
                               'Month': [6, 12],
                               'Day': [8, 22],
                               'Hour': [6, 11],
                               'Minute': [6, 58]})
    wrapper.parse_datetime()
    assert(all(
        wrapper.df.dt == pd.to_datetime(['19900608 06:06',
                                         '20011222 11:58'])
    ))


def test_addsolar_angles():
    """Test to add soalr angles to dateframe based on location and datetime"""
    wrapper = EndpointWrapper('test_url', (40, 60), {'a': 'b'})
    wrapper.df = pd.DataFrame({'Year': [1990, 2001],
                               'Month': [6, 12],
                               'Day': [8, 22],
                               'Hour': [6, 11],
                               'Minute': [6, 58]})
    wrapper.parse_datetime()
    # Datetime object needs to be timezone aware for pysolar
    wrapper.df.dt = wrapper.df.dt.dt.tz_localize('utc')
    wrapper.add_zenith_azimuth()
    assert np.allclose(wrapper.df.zenith, np.array([60.633073, 5.734261]))
    assert np.allclose(wrapper.df.azimuth, np.array([117.275751, 232.854722]))
