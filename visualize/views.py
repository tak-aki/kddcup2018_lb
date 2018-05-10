from django.shortcuts import render
import pandas as pd
from datetime import timedelta
import logging
import os

logger = logging.getLogger(__name__)

# Create your views here.
def visualize_view(request):
	# label data
    label_data = {}
    for city in ['beijing','london']:
        dir_name = "bj" if city == "beijing" else "ld"
        temp_label_data = pd.DataFrame(index=[], columns=['station_id','record_time','PM2.5','PM10','NO2','CO','O3','SO2'])
        for p in pd.date_range('20180415','20180531'):
        	path = "./competition_data/data/official_aq_master/"+dir_name+"/date/"+p.strftime("%Y-%m-%d") + ".csv"
        	if os.path.exists(path):
	            temp = pd.read_csv(path)
	            temp_label_data = pd.concat([temp_label_data,temp],axis=0)
        temp_label_data = temp_label_data.loc[:,['record_time','PM2.5','PM10','O3']].groupby(['record_time']).median()
        # 先頭行がnullだと怒られるからとりあえず
        temp_label_data.iloc[0, :] = 0
        label_data[city] = temp_label_data

    charts = []
    for city in ['beijing','london']:
        targets = ['PM2.5','PM10','O3'] if city == "beijing" else ['PM2.5','PM10']
        for target in targets:
            temp_dict = {'city':city,'target':target}
            temp_dict['chart_data_series'] = []
            temp_dict['chart_data_series'].append({
                'name':'median',
                'data':str(label_data[city][target].values.tolist()).replace('nan','null'),
                'start_dt':str(label_data[city].index[0])
                })
            charts.append(temp_dict)
    
    context = {
        'charts': charts,
    }

    return render(request, 'visualize/datachart.html', context)

# detail view
def visualize_detail_view(request):
    city = request.GET['city']
    target = request.GET['target']
	# data load
    dir_name = "bj" if city == "beijing" else "ld"
    label_data = pd.DataFrame(index=[], columns=['station_id','record_time','PM2.5','PM10','NO2','CO','O3','SO2'])
    for p in pd.date_range('20180415','20180531'):
        path = "./competition_data/data/official_aq_master/"+dir_name+"/date/"+p.strftime("%Y-%m-%d") + ".csv"
        if os.path.exists(path):
            temp = pd.read_csv(path)
            label_data = pd.concat([label_data,temp],axis=0)
    label_data_stations = {}
    for station in label_data['station_id'].unique():
        temp_label_data = label_data.loc[label_data['station_id'] == station,['record_time',target]].set_index('record_time')
        # 先頭行がnullだと怒られるからとりあえず
        temp_label_data.iloc[0, :] = 0
        # データに抜けがあるので、ガワを作る
        # ただ、最初のほうがnanだと怒られるので、最初の方のnanがない時間帯から始める
        #temp = pd.DataFrame(index=pd.date_range(temp_label_data.index[0],(pd.to_datetime(score_date) + timedelta(days = 3)).strftime("%Y-%m-%d") + ' 23:00:00', freq='H'))
        #temp_label_data = temp_label_data.join(temp,how="outer")
        label_data_stations[station] = temp_label_data

    charts = []
    for station in sorted(label_data_stations.keys()):
        temp_dict = {'station':station}
        temp_dict['chart_data_series'] = []
        temp_dict['chart_data_series'].append({
            'name':'label',
            'data':str(label_data_stations[station].values.tolist()).replace('nan','null'),
            'start_dt':str(label_data_stations[station].index[0])
            })
        charts.append(temp_dict)

    context = {
        'charts': charts,
        'city' : city,
        'target' : target
    }

    return render(request, 'visualize/datachart_detail.html', context)
