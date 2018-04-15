from django.urls import path
from mysubmission import views

app_name = 'mysubmission'
urlpatterns = [
    path('', views.mysubmission_base_view, name='mysubmission_base_view'),
    path('detail', views.mysubmission_detail_view, name='mysubmission_detail_view'),
]
