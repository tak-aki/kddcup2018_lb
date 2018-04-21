from django.shortcuts import render, redirect
from submit.models import ScoreModel, SubmitModel
import pandas as pd
from datetime import timedelta

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
        return redirect('/mysubmission/')

    submit_id = request.POST['submit_id']
    submit_timestamp = request.POST['submit_timestamp']
    submit_username = request.POST['submit_username']
    submit_filename = request.POST['submit_filename']
    scores = ScoreModel.objects.filter(submit=submit_id)

    # for chart
    submit = SubmitModel.objects.filter(id=submit_id)[0]

    # label data
    label_data = {}
    for city in ['beijing','london']:
        dir_name = "bj" if city == "beijing" else "ld"
        temp_label_data = pd.DataFrame(index=[], columns=['station_id','record_time','PM2.5','PM10','NO2','CO','O3','SO2'])
        for p in pd.date_range(submit.score_date_start - timedelta(days = 7),submit.score_date_end + timedelta(days = 2)):
            temp = pd.read_csv("./competition_data/data/official_aq_master/"+dir_name+"/date/"+p.strftime("%Y-%m-%d") + ".csv")
            temp_label_data = pd.concat([temp_label_data,temp],axis=0)
        temp_label_data = temp_label_data.loc[:,['record_time','PM2.5','PM10','O3']].groupby(['record_time']).median()
        # 先頭行がnullだと怒られるからとりあえず
        temp_label_data.iloc[0, :] = 0
        # データに抜けがあるので、ガワを作る
        # ただ、最初のほうがnanだと怒られるので、最初の方のnanがない時間帯から始める
        temp = pd.DataFrame(index=pd.date_range(temp_label_data.index[0],(submit.score_date_end + timedelta(days = 2)).strftime("%Y-%m-%d") + ' 23:00:00', freq='H'))
        temp_label_data = temp_label_data.join(temp,how="outer")
        label_data[city] = temp_label_data

    # submit data
    submit_data_series = []
    submit_data = pd.read_csv("./submit/static/submit_files/"+submit.username+"/"+submit.filename)
    submit_data['stationId'] = submit_data['test_id'].str.split('#').apply(lambda x:x[0])
    submit_data['hour_num'] = submit_data['test_id'].str.split('#').apply(lambda x:x[1]).astype(int)
    # score_dateごとに処理
    for score_date in submit_data['score_date'].unique():
        base_datetime = pd.to_datetime(score_date) + timedelta(days = 1)
        temp_submit = submit_data.loc[submit_data['score_date'] == score_date]
        temp_submit['datetime'] = temp_submit['hour_num'].apply(lambda x:base_datetime + timedelta(hours = x))
        temp_submit_beiijng = temp_submit.loc[temp_submit['stationId'].str.contains('_aq')]
        temp_submit_beiijng = temp_submit_beiijng.loc[:,['datetime','PM2.5','PM10','O3']].groupby(['datetime']).median()
        temp_submit_london = temp_submit.loc[~temp_submit['stationId'].str.contains('_aq')]
        temp_submit_london = temp_submit_london.loc[:,['datetime','PM2.5','PM10','O3']].groupby(['datetime']).median()
        temp_submit_data = {}
        temp_submit_data['base_datetime'] = base_datetime
        temp_submit_data['beijing'] = temp_submit_beiijng
        temp_submit_data['london'] = temp_submit_london
        temp_submit_data['date'] = score_date
        submit_data_series.append(temp_submit_data)

    charts = []
    for city in ['beijing','london']:
        targets = ['PM2.5','PM10','O3'] if city == "beijing" else ['PM2.5','PM10']

        for target in targets:
            temp_dict = {'city':city,'target':target}
            temp_dict['chart_data_series'] = []
            temp_dict['chart_data_series'].append({
                'name':'label',
                'data':str(label_data[city][target].values.tolist()).replace('nan','null'),
                'start_dt':str(label_data[city].index[0])
                })
            # ここをsubmitのscoreごとにループ
            for sd in submit_data_series:
                temp_dict['chart_data_series'].append({
                    'name':'submit ' + sd['date'],
                    'data':str(sd[city][target].values.tolist()).replace('nan',''),
                    'start_dt':sd['base_datetime']
                    })
            charts.append(temp_dict)

    context = {
        'charts': charts,
        'scores': scores,
        'submit_id': submit_id,
        'submit_timestamp' : submit_timestamp,
        'submit_username' : submit_username,
        'submit_filename' : submit_filename,
    }

    return render(request, 'mysubmission/mysubmission_detail.html', context)