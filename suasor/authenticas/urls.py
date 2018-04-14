from django.conf.urls import url
from django.contrib import admin

from . import views

app_name = 'authenticas'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^novus/', views.signup, name='signup'),
]
