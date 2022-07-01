from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=256)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user", blank=True, null=True)
    is_active = models.BooleanField(default=True)


class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_groups")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="user_groups")
    is_admin = models.BooleanField(default=False)
    is_extra_user = models.BooleanField(default=False)


class Comment(models.Model):
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments", blank=True, null=True)
    event = models.ForeignKey('User.Event', on_delete=models.CASCADE, related_name="user_comments", blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_comments", blank=True, null=True)

    def __str__(self):
        return f"{self.create_date.strftime('%d/%m/%Y, %H:%M')} - {self.group_id}"
