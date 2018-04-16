from django.shortcuts import render, redirect
from submit.models import ScoreModel, SubmitModel

# Create your views here.
def leaderboard_base_view(request):

    score_list = ScoreModel.objects.all()
    date_list = score_list.values_list('score_date', flat=True).distinct()

    context = {
        'date_list':date_list,
        'score_list':score_list
    }

    return render(request, 'leaderboard/leaderboard_list.html', context)