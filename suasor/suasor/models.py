from django.db import models


class Friendship(models.Model):
    user1 = models.TextField()
    user2 = models.TextField()


class LogType(models.Model):
    name = models.CharField(max_length=10)


class Log(models.Model):
    at_time = models.CharField(max_length=27)
    type = models.ForeignKey(LogType)
    in_package = models.TextField()
    in_function = models.TextField()
    description = models.TextField()


class Rating(models.Model):
    user1 = models.TextField()
    user2 = models.TextField()
    grade = models.NullBooleanField()
    trainset = models.NullBooleanField()


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
    has_saved_picture = models.BooleanField(default=False)
