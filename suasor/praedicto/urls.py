from django.conf.urls import url
from django.contrib import admin

from . import views
from .auxilium import TRAIN_SET_SIZE

app_name = 'praedicto'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^train/$', views.train, name='train'),
    url(r'^train/(?P<user_id>[0-9a-zA-Z.]+)\\?(?P<grades>[01]{%s})/$' % TRAIN_SET_SIZE, views.train, name='train_finished'),
]
