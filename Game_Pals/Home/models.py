from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    avatar = models.ImageField(default='avatars/random_avatar.jpg', upload_to="avatars")
    personal_info = models.TextField(blank=True, null=True)
    # Line below is for later to improve FRIENDS MECHANISMS
    # friends = models.ManyToManyField(User, related_name='friends', blank=True)


class Game(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(null=True)
    image = models.ImageField(blank=True, null=True)
    user = models.ManyToManyField(User, related_name='games', through='UserGames')


class UserGames(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)

