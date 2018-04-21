from django.shortcuts import render, redirect
from submit.models import ScoreModel, SubmitModel
import pandas as pd

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
    score_html_df = score_df.astype(str)
    min_score_indices = score_df.idxmin(axis=0)
    for c, i in min_score_indices.iteritems():
        score_html_df.loc[i, c] = '<b>' + score_html_df.loc[i, c] + '</b>'


    # 太字表示のための最良スコアのフラグを付ける
    score_flag_dict = score_df.T.to_dict()
    for i in score_flag_dict.keys():
        for c in score_flag_dict[i].keys():
            if min_score_indices[c] == i:
                score_flag_dict[i][c] = {'score':score_df.loc[i,c], 'flag':1}
            else:
                score_flag_dict[i][c] = {'score': score_df.loc[i, c], 'flag': 0}


    context = {
        'simulated_score':simulated_score,
        'submit_list':submit_list,
        'date_list':score_df.columns.tolist(),
        'score_flag':score_flag_dict,
    }
    return render(request, 'scoresimulator/scoresimulator_result.html', context)