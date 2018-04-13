# coding: utf-8

import pandas as pd
import requests
import os

home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir))

for p in ['data', 'data/official_aq_master', 'data/official_aq_master/bj', 'data/official_aq_master/ld',
         'data/official_aq_master/bj/date', 'data/official_aq_master/ld/date']:
    dirpath = os.path.join(home, p)

    if not os.path.exists(dirpath):
        print('create ' + dirpath)
        os.mkdir(dirpath)


beijing_aq_historical = pd.read_csv(
    os.path.join(home, 'input/beijing_17_18_aq.csv'),
    parse_dates=['utc_time'])\
    .rename(columns={'stationId':'station_id', 'utc_time':'record_time'})\
    .sort_values(['station_id', 'record_time'])


beijing_aq_historical_append = pd.read_csv(
    os.path.join(home, 'input/beijing_201802_201803_aq.csv'),
    parse_dates=['utc_time'])\
    .rename(columns={'stationId':'station_id', 'utc_time':'record_time'})\
    .sort_values(['station_id', 'record_time'])


beijing_aq_historical_20180331 = \
    pd.read_csv('https://biendata.com/competition/airquality/bj/2018-03-31-0/2018-03-31-23/2k0d1d8',
                                            parse_dates=['time'])\
    .rename(columns={
        'time':'record_time', 
        'PM25_Concentration':'PM2.5', 
        'PM10_Concentration':'PM10', 
        'NO2_Concentration':'NO2', 
        'CO_Concentration':'CO', 
        'O3_Concentration':'O3', 
        'SO2_Concentration':'SO2', 
    }).drop('id', axis=1)\
    .sort_values(['station_id', 'record_time'])


beijing_aq_historical_concat = pd.concat([beijing_aq_historical,
                                          beijing_aq_historical_append,
                                          beijing_aq_historical_20180331])\
    .drop_duplicates().sort_values(['station_id', 'record_time']).reset_index(drop=True)


beijing_aq_historical_concat[['station_id', 'record_time', 'PM2.5', 'PM10', 'O3', 'NO2' ,'CO', 'SO2']]\
    .to_csv(os.path.join(home, 'data/official_aq_master/bj/aq_historical.csv'), index=False)


london_aq_historical_forecast = pd.read_csv(
    os.path.join(home, 'input/London_historical_aqi_forecast_stations_20180331.csv'),
    parse_dates=['MeasurementDateGMT'], index_col=0)\
    .rename(columns = {
        'MeasurementDateGMT':'record_time', 
        'PM2.5 (ug/m3)':'PM2.5', 
        'PM10 (ug/m3)':'PM10', 
        'NO2 (ug/m3)':'NO2'
    })\
    .sort_values(['station_id', 'record_time'])


london_aq_historical_other = pd.read_csv(
    os.path.join(home, 'input/London_historical_aqi_other_stations_20180331.csv'),
    parse_dates=['MeasurementDateGMT'], usecols=[0,1,2,3,4])\
    .rename(columns = {
        'Station_ID':'station_id', 
        'MeasurementDateGMT':'record_time', 
        'PM2.5 (ug/m3)':'PM2.5', 
        'PM10 (ug/m3)':'PM10', 
        'NO2 (ug/m3)':'NO2'
    })\
    .sort_values(['station_id', 'record_time'])


london_aq_historical_other = london_aq_historical_other.loc[
    ~(london_aq_historical_other.station_id.isnull() | london_aq_historical_other.record_time.isnull())]


london_aq_historical_20180331 = \
    pd.read_csv('https://biendata.com/competition/airquality/ld/2018-03-31-0/2018-03-31-23/2k0d1d8',
                                            parse_dates=['time'])\
    .rename(columns={
        'time':'record_time', 
        'PM25_Concentration':'PM2.5', 
        'PM10_Concentration':'PM10', 
        'NO2_Concentration':'NO2', 
        'CO_Concentration':'CO', 
        'O3_Concentration':'O3', 
        'SO2_Concentration':'SO2', 
    }).drop('id', axis=1)\
    .sort_values(['station_id', 'record_time'])


london_aq_historical_concat = pd.concat([london_aq_historical_forecast,
                                         london_aq_historical_other,
                                         london_aq_historical_20180331])\
    .drop_duplicates().sort_values(['station_id', 'record_time']).reset_index(drop=True)


london_aq_historical_concat[['station_id', 'record_time', 'PM2.5', 'PM10', 'O3', 'NO2' ,'CO', 'SO2']]\
    .to_csv(os.path.join(home, 'data/official_aq_master/ld/aq_historical.csv'), index=False)

