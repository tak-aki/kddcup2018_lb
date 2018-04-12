from django.urls import path
from submit import views

app_name = 'submit'
urlpatterns = [
    path('', views.submit_form_view, name='submit_form'), 
    path('complete/', views.complete_view, name='complete'), 
]
