from django.urls import path
from scoresimulator import views

app_name = 'scoresimulator'
urlpatterns = [
    path('', views.scoresimulator_base_view, name='scoresimulator_base_view'),
    path('result', views.scoresimulator_result_view, name='scoresimulator_result_view'),
]