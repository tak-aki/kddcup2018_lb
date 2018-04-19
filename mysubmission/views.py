from django.shortcuts import render, redirect
from submit.models import ScoreModel, SubmitModel
import json
import pandas as pd
from datetime import date, timedelta

# Create your views here.
def mysubmission_base_view(request):
    if request.method != 'POST':
        return render(request, 'mysubmission/mysubmission_base.html')

    # ユーザ名を入手
    username = request.POST['username']

    submits = SubmitModel.objects.filter(username=username)
    context = {'submits': submits}

    return render(request, 'mysubmission/mysubmission_list.html', context)

def mysubmission_detail_view(request):
    if request.method != 'POST':
        return redirect(mysubmission_base_view)

    submit_id = request.POST['submit_id']
    submit_timestamp = request.POST['submit_timestamp']
    submit_username = request.POST['submit_username']
    submit_filename = request.POST['submit_filename']
    scores = ScoreModel.objects.filter(submit=submit_id)

    # for chart
    submit = SubmitModel.objects.filter(id=submit_id)

    for index, score in enumerate(scores):
        # submit data
        submit_data = pd.read_csv("./submit/static/submit_files/"+submit[0].username+"/"+submit[0].filename)
        submit_data['stationId'] = submit_data['test_id'].str.split('#').apply(lambda x:x[0])
        submit_data['hour_num'] = submit_data['test_id'].str.split('#').apply(lambda x:x[1]).astype(int)
        base_datetime = pd.to_datetime(scores[index].score_date) + timedelta(days = 1)
        submit_data['datetime'] = submit_data['hour_num'].apply(lambda x:base_datetime + timedelta(hours = x))
        submit_data_beiijng = submit_data.loc[submit_data['stationId'].str.contains('_aq')]
        submit_data_beiijng = submit_data_beiijng.loc[:,['datetime','PM2.5','PM10','O3']].groupby(['datetime']).median()
        submit_data_london = submit_data.loc[~submit_data['stationId'].str.contains('_aq')]
        submit_data_london = submit_data_london.loc[:,['datetime','PM2.5','PM10','O3']].groupby(['datetime']).median()
        submit_data = {}
        submit_data['beijing'] = submit_data_beiijng
        submit_data['london'] = submit_data_london

        # label data
        label_data = {}
        for city in ['beijing','london']:
            dir_name = "bj" if city == "beijing" else "ld"
            temp_label_data = pd.DataFrame(index=[], columns=['station_id','record_time','PM2.5','PM10','NO2','CO','O3','SO2'])
            for p in pd.date_range(score.score_date - timedelta(days = 7),score.score_date + timedelta(days = 2)):
                temp = pd.read_csv("./competition_data/data/official_aq_master/"+dir_name+"/date/"+p.strftime("%Y-%m-%d") + ".csv")
                temp_label_data = pd.concat([temp_label_data,temp],axis=0)
            temp_label_data = temp_label_data.loc[:,['record_time','PM2.5','PM10','O3']].groupby(['record_time']).median()
            # 先頭行がnullだと怒られるからとりあえず
            temp_label_data.iloc[0, :] = 0
            # データに抜けがあるので、ガワを作る
            # ただ、最初のほうがnanだと怒られるので、最初の方のnanがない時間帯から始める
            temp = pd.DataFrame(index=pd.date_range(temp_label_data.index[0],(score.score_date + timedelta(days = 2)).strftime("%Y-%m-%d") + ' 23:00:00', freq='H'))
            temp_label_data = temp_label_data.join(temp,how="outer")
            label_data[city] = temp_label_data

        scores[index].charts = []
        for city in ['beijing','london']:
            targets = ['PM2.5','PM10','O3'] if city == "beijing" else ['PM2.5','PM10']

            for target in targets:
                temp_dict = {'city':city,'target':target}
                temp_dict['chart_data_series'] = []
                temp_dict['chart_data_series'].append({
                    'name':'submit',
                    'data':str(submit_data[city][target].values.tolist()).replace('nan',''),
                    'start_dt':base_datetime
                    })
                temp_dict['chart_data_series'].append({
                    'name':'label',
                    'data':str(label_data[city][target].values.tolist()).replace('nan','null'),
                    'start_dt':str(label_data[city].index[0])
                    })
                scores[index].charts.append(temp_dict)

    context = {
        'scores': scores,
        'submit_id': submit_id,
        'submit_timestamp' : submit_timestamp,
        'submit_username' : submit_username,
        'submit_filename' : submit_filename,
    }

    return render(request, 'mysubmission/mysubmission_detail.html', context)