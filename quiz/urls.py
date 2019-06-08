from django.conf.urls import url

from quiz import views

__author__ = 'Akhilez'

app_name = 'quiz'

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^home/', views.home, name="home"),
    url(r'^authenticate/', views.authenticate, name='authenticate'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^sign_up/', views.sign_up, name='sign_up'),
    url(r'^reset_password/', views.reset_password, name='reset_password'),
    url(r'^start/([A-Za-z0-9]+)/$', views.start_quiz, name='start'),
    url(r'^mock/$', views.mock_quiz, name='mock'),
]
