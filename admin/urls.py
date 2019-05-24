from django.conf.urls import url

from admin import views

__author__ = 'Akhilez'

urlpatterns = [
    url(r'^$', views.admin_home, name="admin.home"),
]
