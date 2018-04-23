from django.shortcuts import render, redirect
from submit.models import ScoreModel, SubmitModel
import pandas as pd
from datetime import timedelta

def scoresimulator_base_view(request):

    ss_submits = SubmitModel.objects.filter(for_score_simulation=True)
    context = {'ss_submits': ss_submits}

    return render(request, 'scoresimulator/scoresimulator_base.html', context)

def scoresimulator_result_view(request):
    if request.method != 'POST':
        return redirect('/scoresimulator/')

    submit_id_list = request.POST.getlist('scoresimulate')

    # 一つも選択していなかったらエラー
    if len(submit_id_list) == 0:
        ##### 処理
        raise NotImplementedError('一つも選択されていない')

    # 4つ以上選択していたらエラー
    if len(submit_id_list) > 3:
        ##### 処理
        raise NotImplementedError('4つ以上選択されている')

    # スコアの読み込み
    score_df_list = []
    submit_list = []
    for submit_id in submit_id_list:
        submit_list.append(SubmitModel.objects.filter(id=submit_id)[0])
        score_list = ScoreModel.objects.filter(submit=submit_id)

        score_sr = pd.Series()
        for score in score_list:
            score_sr[score.score_date] = score.score
        score_df_list.append(score_sr.to_frame(name=submit_id).T)
    score_df = pd.concat(score_df_list).fillna(2)

    # 各日程の最良スコアを選択してスコアをシミュレーション
    simulated_score = score_df.min(axis=0).mean()

    # 太字表示のための最良スコアのフラグを付ける
    min_score_indices = score_df.idxmin(axis=0)
    score_flag_dict = score_df.T.to_dict()
    for i in score_flag_dict.keys():
        for c in score_flag_dict[i].keys():
            if min_score_indices[c] == i:
                score_flag_dict[i][c] = {'score':score_df.loc[i,c], 'flag':1}
            else:
                score_flag_dict[i][c] = {'score': score_df.loc[i, c], 'flag': 0}

    # for chart
    label_date_start = submit_list[0].score_date_start - timedelta(days = 7)
    label_date_end = submit_list[0].score_date_end + timedelta(days = 2)

    # label data
    label_data = {}
    for city in ['beijing','london']:
        dir_name = "bj" if city == "beijing" else "ld"
        temp_label_data = pd.DataFrame(index=[], columns=['station_id','record_time','PM2.5','PM10','NO2','CO','O3','SO2'])
        for p in pd.date_range(label_date_start, label_date_end):
            temp = pd.read_csv("./competition_data/data/official_aq_master/"+dir_name+"/date/"+p.strftime("%Y-%m-%d") + ".csv")
            temp_label_data = pd.concat([temp_label_data,temp],axis=0)
        temp_label_data = temp_label_data.loc[:,['record_time','PM2.5','PM10','O3']].groupby(['record_time']).median()
        # 先頭行がnullだと怒られるからとりあえず
        temp_label_data.iloc[0, :] = 0
        # データに抜けがあるので、ガワを作る
        # ただ、最初のほうがnanだと怒られるので、最初の方のnanがない時間帯から始める
        temp = pd.DataFrame(index=pd.date_range(temp_label_data.index[0],label_date_end.strftime("%Y-%m-%d") + ' 23:00:00', freq='H'))
        temp_label_data = temp_label_data.join(temp,how="outer")
        label_data[city] = temp_label_data



    # submit data
    submit_data_dict = {}
    for tmp_submit in submit_list:
        tmp_submit_data = pd.read_csv("./submit/static/submit_files/"+tmp_submit.username+"/"+tmp_submit.filename)
        tmp_submit_data['stationId'] = tmp_submit_data['test_id'].str.split('#').apply(lambda x: x[0])
        tmp_submit_data['hour_num'] = tmp_submit_data['test_id'].str.split('#').apply(lambda x: x[1]).astype(int)
        submit_data_dict[str(tmp_submit.id)] = tmp_submit_data


    # score_dateごとに処理
    selected_data_list = []
    for score_date in score_df.columns.tolist():
        selected_id = min_score_indices[score_date]

        base_datetime = pd.to_datetime(score_date) + timedelta(days = 1)
        temp_submit = submit_data_dict[selected_id]
        temp_submit = temp_submit.loc[temp_submit['score_date'] == score_date.strftime("%Y-%m-%d")]
        temp_submit['datetime'] = temp_submit['hour_num'].apply(lambda x:base_datetime + timedelta(hours = x))
        temp_submit_beijng = temp_submit.loc[temp_submit['stationId'].str.contains('_aq')]
        temp_submit_beijng = temp_submit_beijng.loc[:,['datetime','PM2.5','PM10','O3']].groupby(['datetime']).median()
        temp_submit_london = temp_submit.loc[~temp_submit['stationId'].str.contains('_aq')]
        temp_submit_london = temp_submit_london.loc[:,['datetime','PM2.5','PM10','O3']].groupby(['datetime']).median()

        temp_submit_data = {}
        temp_submit_data['selected_id'] = selected_id
        temp_submit_data['base_datetime'] = base_datetime
        temp_submit_data['beijing'] = temp_submit_beijng
        temp_submit_data['london'] = temp_submit_london
        temp_submit_data['date'] = score_date.strftime("%m-%d")
        selected_data_list.append(temp_submit_data)

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
            for sd in selected_data_list:
                temp_dict['chart_data_series'].append({
                    'name':'date:' + sd['date'] + ' id:' + sd['selected_id'],
                    'data':str(sd[city][target].values.tolist()).replace('nan',''),
                    'start_dt':sd['base_datetime']
                    })
            charts.append(temp_dict)

    context = {
        'charts': charts,
        'simulated_score':simulated_score,
        'submit_list':submit_list,
        'date_list':score_df.columns.tolist(),
        'score_flag':score_flag_dict,
    }
    return render(request, 'scoresimulator/scoresimulator_result.html', context)