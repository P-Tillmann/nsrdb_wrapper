# -*- coding: utf-8 -*-

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='nsrdb_wrapper',
      version='0.1',
      description='''This package should provide easy access to data from
      The National Solar Radiation Database provided by NREL.
      Data gets provided as pandas dataframes.''',
      long_description=readme(),
      url='https://github.com/P-Tillmann/nsrdb_wrapper',
      author='Peter Tillmann',
      author_email='Peter.tillmann@helmholtz-berlin.de',
      license='MIT',
      packages=['nsrdb_wrapper'],
      setup_requires=['pytest-runner'],
      test_require=['pytest'],
      install_requires=[
          'pandas', 'pysolar', 'pyyaml', 'requests'
      ],
      zip_safe=False)
