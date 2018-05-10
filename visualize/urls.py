from django.urls import path
from visualize import views

app_name = 'visualize'
urlpatterns = [
    path('', views.visualize_view, name='visualize_view'),
    path('detail', views.visualize_detail_view, name='visualize_detail_view'),
]