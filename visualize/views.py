from django.shortcuts import render

# Create your views here.
def visualize_view(request):
    return render(request, 'visualize/datachart.html')
