from django.conf.urls import url
from django.contrib import admin

from . import views

app_name = 'praedicto'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
