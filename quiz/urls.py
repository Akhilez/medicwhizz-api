from django.conf.urls import url

from quiz import views

__author__ = 'Akhilez'

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^home/', views.home, name="home"),
    url(r'^authenticate/', views.authenticate, name='authenticate'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^sign_up/', views.sign_up, name='sign_up'),
    url(r'^reset_password/', views.reset_password, name='reset_password'),
]
