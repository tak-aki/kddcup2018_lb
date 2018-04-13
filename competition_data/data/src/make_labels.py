# coding: utf-8

import pandas as pd
import os

home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir))
ld_forecast_stationid = pd.read_csv(\
    os.path.join(home, 'input', 'London_historical_aqi_forecast_stations_20180331.csv'))['station_id'].unique().tolist()
bj_submission_stationid_convert_dict = {
    'aotizhongxin_aq' : 'aotizhongx_aq',
    'fengtaihuayuan_aq' : 'fengtaihua_aq',
    'miyunshuiku_aq' : 'miyunshuik_aq',
    'nongzhanguan_aq' : 'nongzhangu_aq',
    'wanshouxigong_aq' : 'wanshouxig_aq',
    'xizhimenbei_aq' : 'xizhimenbe_aq',
    'yongdingmennei_aq' : 'yongdingme_aq'
}

# ラベルディレクトリがなかったら作成
label_dirpath = os.path.join(home, 'data', 'labels')
if not os.path.exists(label_dirpath):
    print('create ' + label_dirpath)
    os.mkdir(label_dirpath)
# 空気データのディレクトリ
aqdata_bj_dirpath = os.path.join(home, 'data', 'official_aq_master', 'bj', 'date')
aqdata_ld_dirpath = os.path.join(home, 'data', 'official_aq_master', 'ld', 'date')

# すでに作成されたlabelの日付リスト
label_date_list = [file[:-4] for file in os.listdir(label_dirpath)]
# 作成可能なdataの日付リスト(最新日が含まれるラベル日付は除く)
aqdata_bj_date_list = pd.Series([file[:-4] for file in os.listdir(aqdata_bj_dirpath)])
aqdata_ld_date_list = pd.Series([file[:-4] for file in os.listdir(aqdata_ld_dirpath)])
aqdata_date_list = aqdata_bj_date_list.loc[aqdata_bj_date_list.isin(aqdata_ld_date_list)].sort_values().iloc[:-3]
# 作成すべき日のリスト
make_date_list = aqdata_date_list.loc[~aqdata_date_list.isin(label_date_list)].tolist()

for date in make_date_list:
    print('create label:' + date)

    # データに含まれるべき時間帯
    range_start = pd.to_datetime(date) + pd.DateOffset(1)
    range_end = range_start + pd.DateOffset(2) - pd.Timedelta(hours=1)

    # データ読み込み
    bj_aq = pd.concat([
        pd.read_csv(os.path.join(aqdata_bj_dirpath, str(range_start.date()) + '.csv'), parse_dates=['record_time']),
        pd.read_csv(os.path.join(aqdata_bj_dirpath, str(range_end.date()) + '.csv'), parse_dates=['record_time'])])\
        .reset_index(drop=True)
    bj_aq['station_id'] = bj_aq.station_id.replace(bj_submission_stationid_convert_dict)

    ld_aq = pd.concat([
        pd.read_csv(os.path.join(aqdata_ld_dirpath, str(range_start.date()) + '.csv'), parse_dates=['record_time']),
        pd.read_csv(os.path.join(aqdata_ld_dirpath, str(range_end.date()) + '.csv'), parse_dates=['record_time'])])\
        .reset_index(drop=True)
    ld_aq = ld_aq.loc[ld_aq.station_id.isin(ld_forecast_stationid)]

    # 時間的欠損埋め
    bj_aq_base = pd.DataFrame(index=pd.MultiIndex.from_product(
        [bj_aq['station_id'].unique(),
         pd.date_range(range_start, range_end, freq='h')],
        names=['station_id', 'record_time'])).reset_index()
    bj_aq = bj_aq_base.merge(bj_aq, how='left').sort_values(['station_id', 'record_time'])

    ld_aq_base = pd.DataFrame(index=pd.MultiIndex.from_product(
        [ld_aq['station_id'].unique(),
         pd.date_range(range_start, range_end, freq='h')],
        names=['station_id', 'record_time'])).reset_index()
    ld_aq = ld_aq_base.merge(ld_aq, how='left').sort_values(['station_id', 'record_time'])

    # ファイルの連結
    concat_aq = pd.concat([bj_aq, ld_aq])

    # test_idの作成
    concat_aq['hour_index'] = ((concat_aq.record_time - range_start).dt.total_seconds() // 3600).astype(int)
    concat_aq['test_id'] = concat_aq['station_id'] + '#' + concat_aq['hour_index'].astype(str)

    concat_aq[['test_id', 'PM2.5', 'PM10', 'O3']].to_csv(os.path.join(home, 'data', 'labels', date+'.csv'), index=False)