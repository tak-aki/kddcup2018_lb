from django.shortcuts import render, redirect
from submit.models import ScoreModel, SubmitModel

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
    context = {
        'scores': scores,
        'submit_id': submit_id,
        'submit_timestamp' : submit_timestamp,
        'submit_username' : submit_username,
        'submit_filename' : submit_filename,
    }

    return render(request, 'mysubmission/mysubmission_detail.html', context)