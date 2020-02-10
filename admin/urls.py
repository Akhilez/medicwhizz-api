from django.conf.urls import url
from django.urls import path

from admin import views

__author__ = 'Akhilez'

app_name = 'admin'

urlpatterns = [
    url(r'^$', views.admin_home, name="home"),
    url(r'^add_mock/', views.add_mock, name="add_mock"),
    url(r'^edit_mock/([A-Za-z0-9]+)/$', views.edit_mock, name="edit_mock"),
    url(r'^edit_mock/([A-Za-z0-9]+)/([A-Za-z0-9]+)/$', views.edit_mock_question, name="edit_mock_question"),
]
