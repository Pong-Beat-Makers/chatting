from django.db import models

# Create your models here.

class ChattingUser(models.Model):
    nickname = models.CharField(max_length=15, unique=True)
    is_online = models.BooleanField(default=False)
    channel_name = models.CharField(max_length=100, null=True, default=None)
    blocked_users = models.ManyToManyField('self', symmetrical=False)
