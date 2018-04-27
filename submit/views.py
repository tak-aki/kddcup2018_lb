from django.shortcuts import render, redirect
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
    bj_sape_df = sape_df.loc[sape_df.index.str.contains('_aq#')]
    ld_sape_df = sape_df.loc[~sape_df.index.str.contains('_aq#')]
    bj_pm25_smape = bj_sape_df['PM2.5'].dropna().mean()
    bj_pm10_smape = bj_sape_df['PM10'].dropna().mean()
    bj_o3_smape = bj_sape_df['O3'].dropna().mean()
    ld_pm25_smape = ld_sape_df['PM2.5'].dropna().mean()
    ld_pm10_smape = ld_sape_df['PM10'].dropna().mean()


    sape_array = sape_df.values.reshape([-1])
    smape = sape_array[~np.isnan(sape_array)].mean()

    return smape, bj_pm25_smape, bj_pm10_smape, bj_o3_smape, ld_pm25_smape, ld_pm10_smape

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

    # stationId の変換（旧フォーマットを新フォーマットに変換）
    bj_submission_stationid_convert_dict = {
        'aotizhongx_aq': 'aotizhongxin_aq',
        'fengtaihua_aq': 'fengtaihuayuan_aq',
        'miyunshuik_aq': 'miyunshuiku_aq',
        'nongzhangu_aq': 'nongzhanguan_aq',
        'wanshouxig_aq': 'wanshouxigong_aq',
        'xizhimenbe_aq': 'xizhimenbei_aq',
        'yongdingme_aq': 'yongdingmennei_aq'
    }

    submit_file_df['station_id'] = submit_file_df['test_id'].str.split('#').apply(lambda x: x[0])
    submit_file_df['hour_num'] = submit_file_df['test_id'].str.split('#').apply(lambda x: x[1])
    submit_file_df['station_id'] = submit_file_df['station_id'].replace(bj_submission_stationid_convert_dict)
    submit_file_df['test_id'] = submit_file_df['station_id'] + '#' + submit_file_df['hour_num']
    submit_file_df.drop(['station_id', 'hour_num'], axis=1, inplace=True)
    submit_file_df.to_csv(filepath, index=False)

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
        raise NotImplementedError('数値にNoneがある')

    # 日付リストを取得
    score_date_list = submit_file_df.score_date.unique()

    # score_dateのフォーマットが所定のものでなかったらエラーページを表示
    date_check_sr = pd.Series(score_date_list).apply(
        lambda x: 1 if re.match('^\d{4}-\d{2}-\d{2}$', x) else 0)
    if date_check_sr.sum() != date_check_sr.shape[0]:
        ##### 処理
        raise NotImplementedError('score_dateのフォーマットが違う')

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

    unscored_date_list = []
    for sdate in score_date_list:
        if score_d[sdate]['label'] is None:
            unscored_date_list.append(sdate)

    # スコアリングできる日が1日もなかったらエラー
    if len(score_date_list) == len(unscored_date_list):
        ##### 処理
        raise NotImplementedError('スコアリングできる日が1日もありません。')


    # scoreを計算
    for sdate in score_date_list:
        if score_d[sdate]['submit'] is None:
            score_d[sdate]['score'] = '正解データなし'
        else:
            score, bj_pm25_score, bj_pm10_score, bj_o3_score, ld_pm25_score, ld_pm10_score = \
                calc_smape(score_d[sdate]['label'], score_d[sdate]['submit'])
            score_d[sdate]['score'] = score
            score_d[sdate]['bj_pm25_score'] = bj_pm25_score
            score_d[sdate]['bj_pm10_score'] = bj_pm10_score
            score_d[sdate]['bj_o3_score'] = bj_o3_score
            score_d[sdate]['ld_pm25_score'] = ld_pm25_score
            score_d[sdate]['ld_pm10_score'] = ld_pm10_score


    # 「スコアシミュレーターに使う」にチェックが入っている場合、日付をチェック
    for_score_simulation = request.POST.get('for_score_simulation', False)
    if for_score_simulation:
        for_score_simulation = True
        scoresimulator_datelist = pd.date_range('2018-03-24', '2018-04-20', freq='D').astype(str).tolist()
        if sorted(score_date_list) != sorted(scoresimulator_datelist):
            ##### 処理
            raise NotImplementedError('日付が足りないor多すぎます（スコアシミュレーター用）')
        if len(unscored_date_list) != 0:
            ##### 処理
            raise NotImplementedError('まだ正解データが揃っていません（スコアシミュレーター用）')


    # average scoreを計算
    score_list = []
    date_list = []
    for sdate in score_date_list:
        if not score_d[sdate]['submit'] is None:
            date_list.append(score_d[sdate]['date'])
            score_list.append(score_d[sdate]['score'])
            score_bj_pm25_list.append(score_d[sdate]['bj_pm25_score'])
            score_bj_pm10_list.append(score_d[sdate]['bj_pm10_score'])
            score_bj_o3_list.append(score_d[sdate]['bj_o3_score'])
            score_ld_pm25_list.append(score_d[sdate]['ld_pm25_score'])
            score_ld_pm10_list.append(score_d[sdate]['ld_pm10_score'])
    avg_score = np.mean(score_list)
    avg_bj_pm25_score = np.mean(score_bj_pm25_list)
    avg_bj_pm10_score = np.mean(score_bj_pm10_list)
    avg_bj_o3_score = np.mean(score_bj_o3_list)
    avg_ld_pm25_score = np.mean(score_ld_pm25_list)
    avg_ld_pm10_score = np.mean(score_ld_pm10_list)
    score_date_start = np.min(date_list)
    score_date_end = np.max(date_list)

    submit_model = SubmitModel(
        username=username,
        filename=submit_file_name,
        submit_timestamp=submit_time,
        score_date_start = score_date_start,
        score_date_end = score_date_end,
        score_avg = avg_score,
        avg_bj_pm25_score=avg_bj_pm25_score,
        avg_bj_pm10_score=avg_bj_pm10_score,
        avg_bj_o3_score=avg_bj_o3_score,
        avg_ld_pm25_score=avg_ld_pm25_score,
        avg_ld_pm10_score=avg_ld_pm10_score,
        for_score_simulation=for_score_simulation
    )
    submit_model.save()

    # scoreを登録
    for sdate in score_date_list:
        if not score_d[sdate]['submit'] is None:
            score_model = ScoreModel(
                submit = submit_model,
                score_date = pd.to_datetime(sdate).date(),
                score = score_d[sdate]['score'],
                bj_pm25_score = score_d[sdate]['bj_pm25_score'],
                bj_pm10_score = score_d[sdate]['bj_pm10_score'],
                bj_o3_score = score_d[sdate]['bj_o3_score'],
                ld_pm25_score = score_d[sdate]['ld_pm25_score'],
                ld_pm10_score = score_d[sdate]['ld_pm10_score'],
                )
            score_model.save()

    # 表示ページへ投げる
    if len(unscored_date_list) > 0:
        context = {'submit_model':submit_model, 'unscored_date_list':unscored_date_list}
    else:
        context = {'submit_model':submit_model, 'unscored_date_list':None}

    return render(request, 'submit/complete.html', context)


def update_view(request):
    submit_filename_list = SubmitModel.objects.order_by('filename').values_list('filename').distinct()


    for submit_filename_org in submit_filename_list:

        samename_submit_id_list = SubmitModel.objects\
            .filter(filename=submit_filename_org[0]).order_by('submit_timestamp').values_list('id', flat=True)

        submit_id = samename_submit_id_list.reverse()[0] #最近のサブミットを採用
        submit = SubmitModel.objects.filter(id=submit_id)[0]

        username = submit.username
        submit_file_name = submit.filename
        submit_time = submit.submit_timestamp
        for_score_simulation = submit.for_score_simulation

        # サブミットファイル保存
        userpath = os.path.join(UPLOAD_DIR, username)
        filepath = os.path.join(userpath, submit_file_name)

        # サブミットファイルを読み込み
        submit_file_df = pd.read_csv(filepath)

        # stationId の変換（旧フォーマットを新フォーマットに変換）
        bj_submission_stationid_convert_dict = {
            'aotizhongx_aq': 'aotizhongxin_aq',
            'fengtaihua_aq': 'fengtaihuayuan_aq',
            'miyunshuik_aq': 'miyunshuiku_aq',
            'nongzhangu_aq': 'nongzhanguan_aq',
            'wanshouxig_aq': 'wanshouxigong_aq',
            'xizhimenbe_aq': 'xizhimenbei_aq',
            'yongdingme_aq': 'yongdingmennei_aq'
        }

        submit_file_df['station_id'] = submit_file_df['test_id'].str.split('#').apply(lambda x: x[0])
        submit_file_df['hour_num'] = submit_file_df['test_id'].str.split('#').apply(lambda x: x[1])
        submit_file_df['station_id'] = submit_file_df['station_id'].replace(bj_submission_stationid_convert_dict)
        submit_file_df['test_id'] = submit_file_df['station_id'] + '#' + submit_file_df['hour_num']
        submit_file_df.drop(['station_id', 'hour_num'], axis=1, inplace=True)

        # 日付リストを取得
        score_date_list = submit_file_df.score_date.unique()

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
                score, bj_pm25_score, bj_pm10_score, bj_o3_score, ld_pm25_score, ld_pm10_score = \
                    calc_smape(score_d[sdate]['label'], score_d[sdate]['submit'])
                score_d[sdate]['score'] = score
                score_d[sdate]['bj_pm25_score'] = bj_pm25_score
                score_d[sdate]['bj_pm10_score'] = bj_pm10_score
                score_d[sdate]['bj_o3_score'] = bj_o3_score
                score_d[sdate]['ld_pm25_score'] = ld_pm25_score
                score_d[sdate]['ld_pm10_score'] = ld_pm10_score

        # average scoreを計算
        score_list = []
        score_bj_pm25_list = []
        score_bj_pm10_list = []
        score_bj_o3_list = []
        score_ld_pm25_list = []
        score_ld_pm10_list = []
        date_list = []
        for sdate in score_date_list:
            if not score_d[sdate]['submit'] is None:
                date_list.append(score_d[sdate]['date'])
                score_list.append(score_d[sdate]['score'])
                score_bj_pm25_list.append(score_d[sdate]['bj_pm25_score'])
                score_bj_pm10_list.append(score_d[sdate]['bj_pm10_score'])
                score_bj_o3_list.append(score_d[sdate]['bj_o3_score'])
                score_ld_pm25_list.append(score_d[sdate]['ld_pm25_score'])
                score_ld_pm10_list.append(score_d[sdate]['ld_pm10_score'])
        avg_score = np.mean(score_list)
        avg_bj_pm25_score = np.mean(score_bj_pm25_list)
        avg_bj_pm10_score = np.mean(score_bj_pm10_list)
        avg_bj_o3_score = np.mean(score_bj_o3_list)
        avg_ld_pm25_score = np.mean(score_ld_pm25_list)
        avg_ld_pm10_score = np.mean(score_ld_pm10_list)
        score_date_start = np.min(date_list)
        score_date_end = np.max(date_list)

        # submitを登録
        submit_file_df.to_csv(filepath, index=False)
        submit_model = SubmitModel(
            id=submit_id,
            username=username,
            filename=submit_file_name,
            submit_timestamp=submit_time,
            score_date_start=score_date_start,
            score_date_end=score_date_end,
            score_avg=avg_score,
            avg_bj_pm25_score=avg_bj_pm25_score,
            avg_bj_pm10_score=avg_bj_pm10_score,
            avg_bj_o3_score=avg_bj_o3_score,
            avg_ld_pm25_score=avg_ld_pm25_score,
            avg_ld_pm10_score=avg_ld_pm10_score,
            for_score_simulation=for_score_simulation
        )
        submit_model.save()

        # 同一名の他のsubmitとscoreを削除
        for del_sub_id in samename_submit_id_list:
            del_sub = SubmitModel.objects.filter(id=del_sub_id)[0]
            del_score_list = ScoreModel.objects.filter(submit=del_sub)
            for del_score in del_score_list:
                del_score.delete()
            del_sub.delete()

        submit_model.save()
        # scoreを登録
        for sdate in score_date_list:
            if not score_d[sdate]['submit'] is None:
                score_model = ScoreModel(
                    submit = submit,
                    score_date = pd.to_datetime(sdate).date(),
                    score = score_d[sdate]['score'],
                    bj_pm25_score = score_d[sdate]['bj_pm25_score'],
                    bj_pm10_score = score_d[sdate]['bj_pm10_score'],
                    bj_o3_score = score_d[sdate]['bj_o3_score'],
                    ld_pm25_score = score_d[sdate]['ld_pm25_score'],
                    ld_pm10_score = score_d[sdate]['ld_pm10_score'],
                    )
                score_model.save()

    return redirect('/submit/')