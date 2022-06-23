from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(null=True)
    start_time = models.DateTimeField()
    user = models.ManyToManyField(User, related_name="user_events", blank=True)
    group = models.ForeignKey("Group.Group", on_delete=models.CASCADE,
                              related_name="group_events", null=True, blank=True)
