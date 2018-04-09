# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Friendship(models.Model):
    user1 = models.TextField(blank=True, null=True)
    user2 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'friendship'


class Log(models.Model):
    at_time = models.CharField(max_length=27, blank=True, null=True)
    type = models.ForeignKey('LogType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    in_package = models.TextField(blank=True, null=True)
    in_function = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'log'


class LogType(models.Model):
    name = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'log_type'


class Rating(models.Model):
    user1 = models.TextField(blank=True, null=True)
    user2 = models.TextField(blank=True, null=True)
    grade = models.NullBooleanField()
    trainset = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'rating'


class UserData(models.Model):
    user_id = models.TextField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    birthday = models.TextField(blank=True, null=True)
    lives_in = models.TextField(blank=True, null=True)
    comes_from = models.TextField(blank=True, null=True)
    study = models.TextField(blank=True, null=True)
    picture_url = models.TextField(blank=True, null=True)
    married = models.NullBooleanField()
    in_relationship = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'user_data'
