from django.db import models

class User(models.Model):
    user_id = models.TextField(primary_key=True)
    password = models.TextField()
