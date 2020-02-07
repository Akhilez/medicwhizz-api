from django.conf.urls import url
from django.urls import path

from api_internal import views

__author__ = 'Akhilez'

app_name = 'api_internal'

urlpatterns = [
    path('get_my_quizzes', views.get_user_quizzes, name='get_user_quizzes'),
]
