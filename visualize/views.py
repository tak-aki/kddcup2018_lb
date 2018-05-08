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
        for p in pd.date_range('20180301','20180531'):
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
