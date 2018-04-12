# coding: utf-8

import pandas as pd
import os
from datetime import datetime,timezone

# データを取ってきて保存
def get_and_save(city, date):
    print('get city:{0} date:{1}'.format(city, date))
    api_url = 'https://biendata.com/competition/airquality/{0}/{1}-0/{1}-23/2k0d1d8'.format(city, date)
    aq = pd.read_csv(api_url, parse_dates=['time'])
    aq = aq.rename(columns={
                        'time':'record_time', 
                        'PM25_Concentration':'PM2.5', 
                        'PM10_Concentration':'PM10', 
                        'NO2_Concentration':'NO2', 
                        'CO_Concentration':'CO', 
                        'O3_Concentration':'O3', 
                        'SO2_Concentration':'SO2', 
                    }).drop('id', axis=1)\
                    .sort_values(['station_id', 'record_time'])
    aq.to_csv('../official_aq_master/{0}/date/{1}.csv'.format(city, date), index=False)

# 今日の日付を取ってくる
now_time = datetime.now(tz=timezone.utc)
today = '{0}-{1:02d}-{2:02d}'.format(now_time.year, now_time.month, now_time.day)


# 3/31から今日までの日付リスト
date_list = pd.date_range('2018-04-01', today, freq='D').astype(str).tolist()


# すでに保存されている日付リスト
file_bj_date_list = [file[:-4] for file in os.listdir('../official_aq_master/bj/date/')]
file_ld_date_list = [file[:-4] for file in os.listdir('../official_aq_master/ld/date/')]

# 保存されていない日は取ってくる
#　今日のぶんははどっちにしろ持ってきて置換する
for d in date_list:
    if d in file_bj_date_list:
        if d == today:
            get_and_save('bj', d)
    else:
        get_and_save('bj', d)
        
    if d in file_ld_date_list:
        if d == today:
            get_and_save('ld', d)
    else:
        get_and_save('ld', d)
