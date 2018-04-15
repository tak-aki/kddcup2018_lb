from django.urls import path
from leaderboard import views

app_name = 'leaderboard'
urlpatterns = [
    path('', views.leaderboard_base_view, name='leaderboard_base_view'),
    #path('list', views.leaderboard_list_view, name='leaderboard_list_view'),
]
