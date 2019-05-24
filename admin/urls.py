from django.conf.urls import url

from admin import views

__author__ = 'Akhilez'

app_name = 'admin'

urlpatterns = [
    url(r'^$', views.admin_home, name="home"),
    url(r'^add_mock/', views.add_mock, name="add_mock"),
    url(r'^edit_mock/(\S+)/', views.edit_mock, name="edit_mock"),
]
