from django.shortcuts import render, redirect
from django.template import Context
from django.conf import settings
from submit.models import SubmitModel, ScoreModel
import os
import pandas as pd
import numpy as np
import re
from datetime import datetime
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/submit_files/'
LABELFILE_DIR = os.path.join(settings.BASE_DIR, 'competition_data', 'data', 'labels')

# 公式のLBスコアと違う
def calc_smape(labels, forecasts):
    # arrange both indices
    forecasts = forecasts.loc[labels.index].copy()

    # calc symmetric absolute percentage error
    sape_df = ((labels - forecasts).abs() / ((labels + forecasts) / 2))

    # set sape value 0 if actual value and forecast value are both 0
    sape_df[(labels == 0) & (forecasts == 0)] = 0

    # form the dataframe in line, drop nan, and calc SMAPE
    sape_array = sape_df.values.reshape([-1])
    smape = sape_array[~np.isnan(sape_array)].mean()

    return smape

def submit_form_view(request):
    if request.method != 'POST':
        return render(request, 'submit/submit_form.html')

    # サブミットファイルのユーザ名とファイル名を入手
    username = request.POST['username']
    submit_file = request.FILES['submit_file']
    submit_file_name = submit_file.name

    submit_time = datetime.now()

    # すでにスコアテーブルに存在するユーザ名とファイル名の
    # 組み合わせだったらエラーページを表示
    ##### 処理

    # サブミットファイル保存
    userpath = os.path.join(UPLOAD_DIR, username)
    if not os.path.exists(userpath):
        os.mkdir(userpath)

    filepath = os.path.join(userpath, submit_file_name)
    with open(filepath, 'wb') as destination:
        for chunk in submit_file.chunks():
            destination.write(chunk)

    # サブミットファイルを読み込み
    submit_file_df = pd.read_csv(filepath)

    # 列の数があってなかったらエラーページを表示
    if submit_file_df.columns.shape != (5,):
        ##### 処理
        raise NotImplementedError('列の数があってない')

    # カラムが要件を満たしていなかったらエラーページを表示
    if pd.Series(['score_date', 'test_id', 'PM2.5', 'PM10', 'O3']).isin(submit_file_df.columns).sum() < 5:
        ##### 処理
        raise NotImplementedError('カラムが要件を満たしていない')

    # 数値にNoneがあったらエラーページを表示
    if submit_file_df.isnull().sum().sum() < 0:
        ##### 処理
        raise NotImplementedError('数値にNone')

    # 日付リストを取得
    score_date_list = submit_file_df.score_date.unique()

    # score_dateのフォーマットが所定のものでなかったらエラーページを表示
    date_check_sr = pd.Series(score_date_list).apply(
        lambda x: 1 if re.match('^\d{4}-\d{2}-\d{2}$', x) else 0)
    if date_check_sr.sum() != date_check_sr.shape[0]:
        ##### 処理
        raise NotImplementedError('score_dateのフォーマットが所定のものでない')

    # 日べつに、サブミットファイルと正解ファイルを辞書に格納
    score_d = {}
    for sdate in score_date_list:
        if os.path.exists(os.path.join(LABELFILE_DIR, sdate+'.csv')):
            score_d[sdate] = {
                'date' : pd.to_datetime(sdate).date(),
                'submit' : submit_file_df\
                    .loc[submit_file_df['score_date'] == sdate, ['test_id', 'PM2.5', 'PM10', 'O3']]\
                    .set_index('test_id'),
                'label' : pd.read_csv(os.path.join(LABELFILE_DIR, sdate+'.csv'), index_col=['test_id'])
            }
        else:
            score_d[sdate] = {
                'date' : pd.to_datetime(sdate).date(),
                'submit' : None,
                'label' : None
            }

    # scoreを計算
    for sdate in score_date_list:
        if score_d[sdate]['submit'] is None:
            score_d[sdate]['score'] = '正解データなし'
        else:
            if score_d[sdate]['label'].shape == score_d[sdate]['submit'].shape:
                score_d[sdate]['score'] = calc_smape(score_d[sdate]['label'], score_d[sdate]['submit'])
            else:
                score_d[sdate]['score'] = '行数がおかしい'

    # average scoreを計算
    score_list = []
    date_list = []
    for sdate in score_date_list:
        date_list.append(score_d[sdate]['date'])
        if not score_d[sdate]['submit'] is None:
            score_list.append(score_d[sdate]['score'])
    avg_score = np.mean(score_list)
    score_date_start = np.min(date_list)
    score_date_end = np.max(date_list)

    submit_model = SubmitModel(
        username=username,
        filename=submit_file_name,
        submit_timestamp=submit_time,
        score_date_start = score_date_start,
        score_date_end = score_date_end,
        score_avg = avg_score
    )
    submit_model.save()

    # scoreを登録
    for sdate in score_date_list:
        score_model = ScoreModel(
            submit = submit_model,
            score_date = pd.to_datetime(sdate).date(),
            score = score_d[sdate]['score']
            )
        score_model.save()

    # 表示ページへ投げる
    context = {'submit_model':submit_model}
    return render(request, 'submit/complete.html', context)

def complete_view(request):
    return render(request, 'submit/complete.html')

# Create your views here.
