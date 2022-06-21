from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=256)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user", blank=True, null=True)
    is_active = models.BooleanField(default=True)
