from django.conf.urls import url

from medicwhizz import views

__author__ = 'Akhilez'

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^requests/ask/', views.ask, name="ask"),
    url(r'^requests/ask_next/', views.ask_next, name="ask_next"),
    url(r'^requests/is_completed/', views.is_completed, name="is_completed"),
    url(r'^requests/answer/', views.answer, name="answer"),
]
