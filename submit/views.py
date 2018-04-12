from django.shortcuts import render, redirect
from submit.models import SubmitFileModel, CalculateScoreModel
import os, time
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/submit_files/'

def submit_form_view(request):
    if request.method != 'POST':
        return render(request, 'submit/submit_form.html')
    
    username = request.POST['username']
    userpath = os.path.join(UPLOAD_DIR, username)
    if not os.path.exists(userpath):
        os.mkdir(userpath)

    submit_file = request.FILES['submit_file']
    filepath = os.path.join(userpath, submit_file.name)
    
    with open(filepath, 'wb') as destination:
        for chunk in submit_file.chunks():
            destination.write(chunk)

    filemodel = SubmitFileModel(username = username, filename = submit_file.name)
    filemodel.save()

    scoremodel = CalculateScoreModel()
    scoremodel.calc()

    return redirect('submit:complete')

def complete_view(request):
    return render(request, 'submit/complete.html')

# Create your views here.
